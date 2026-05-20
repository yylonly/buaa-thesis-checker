"""内容提取器 - 从 PDF 提取页面内容和页码 (使用 PDFMiner.six)"""
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTFigure
from typing import List, Dict


class ContentExtractor:
    """PDF 内容提取器 (使用 PDFMiner.six)"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.total_pages = 0
        self.content_by_page: List[Dict] = []
        self.pdf_to_actual_page_map: Dict[int, int] = {}
        self.average_chars: float = 0.0

    def extract_all(self) -> List[Dict]:
        """提取所有页面内容"""
        # 先统计页数
        page_count = 0
        with open(self.pdf_path, 'rb') as f:
            for page in PDFPage.get_pages(f):
                page_count += 1
        self.total_pages = page_count

        print(f"正在读取 PDF (PDFMiner.six)，共 {self.total_pages} 页...")

        # 使用 extract_text 提取每页文本
        all_text = extract_text(self.pdf_path)

        # 按页面分割 - PDFMiner 返回的是连续文本，需要按页拆分
        # 方法：使用页码模式来分割
        pages_text = self._split_pages_by_number(all_text)

        for i, text in enumerate(pages_text):
            pdf_page = i + 1
            actual_page = self._extract_page_number(text, pdf_page)
            char_count = len(text.strip()) if text else 0
            word_count = len(text.split()) if text else 0
            lines = text.count('\n') if text else 0

            self.content_by_page.append({
                'page': pdf_page,
                'actual_page': actual_page,
                'chars': char_count,
                'words': word_count,
                'lines': lines,
                'text': text,
                'pdf_path': self.pdf_path
            })
            self.pdf_to_actual_page_map[pdf_page] = actual_page

        self.average_chars = (
            sum(c['chars'] for c in self.content_by_page) / len(self.content_by_page)
            if self.content_by_page else 0
        )
        print(f"读取完成，平均每页 {self.average_chars:.1f} 字符\n")
        return self.content_by_page

    def _split_pages_by_number(self, full_text: str) -> List[str]:
        """根据页码将连续文本拆分成页面

        PDFMiner 的 extract_text() 返回连续文本，我们通过页码模式来分割。
        页码通常出现在页面顶部或底部，是独立的数字。
        """
        import re

        pages = []
        # 按行分割
        lines = full_text.split('\n')

        current_page_lines = []
        page_numbers_seen = set()

        for line in lines:
            stripped = line.strip()

            # 检测页码模式：单独一行的1-3位数字
            if re.match(r'^[IVXLCDM]+$', stripped):
                # 罗马数字，可能是页码，跳过
                continue
            if re.match(r'^\d{1,3}$', stripped) and 1 <= int(stripped) <= 200:
                # 这可能是页码
                num = int(stripped)
                if num not in page_numbers_seen or num > len(pages) + 1:
                    # 保存当前页
                    if current_page_lines:
                        pages.append('\n'.join(current_page_lines))
                    current_page_lines = []
                    page_numbers_seen.add(num)
                    continue

            current_page_lines.append(line)

        # 最后一页
        if current_page_lines:
            pages.append('\n'.join(current_page_lines))

        # 如果分割失败（页数不对），直接按总页数均分
        if len(pages) != self.total_pages and self.total_pages > 0:
            # 回退方案：直接使用 extract_pages
            return self._extract_pages_fallback()

        return pages

    def _extract_pages_fallback(self) -> List[str]:
        """回退方案：逐页提取"""
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer

        pages = []
        for page_layout in extract_pages(self.pdf_path):
            page_text = []
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text.append(element.get_text())
            pages.append('\n'.join(page_text))

        # 如果页数还是不匹配，直接用单页提取
        if len(pages) != self.total_pages:
            pages = []
            with open(self.pdf_path, 'rb') as f:
                for page in PDFPage.get_pages(f):
                    # 使用默认方法提取单页
                    pass
            # 最终回退：直接提取所有文本然后按长度分页
            all_text = extract_text(self.pdf_path)
            avg_len = len(all_text) // self.total_pages if self.total_pages > 0 else 1000
            for i in range(self.total_pages):
                start = i * avg_len
                end = start + avg_len if i < self.total_pages - 1 else len(all_text)
                pages.append(all_text[start:end])

        return pages

    def _extract_page_number(self, text: str, fallback_pdf_page: int) -> int:
        """从页面文本中提取实际页码"""
        if not text:
            return fallback_pdf_page

        import re
        lines = text.split('\n')

        for line in lines[:3]:
            line = line.strip()
            if line.isdigit() and 1 <= int(line) <= 200:
                return int(line)

        for line in lines[-3:]:
            line = line.strip()
            if line.isdigit() and 1 <= int(line) <= 200:
                return int(line)

        return fallback_pdf_page


def extract_with_positions(pdf_path: str) -> List[Dict]:
    """提取每页文本及其位置信息（字体、字号等）"""
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer, LTTextLine, LTChar, LTFigure

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    pages_data = []

    with open(pdf_path, 'rb') as f:
        for page_num, page in enumerate(PDFPage.get_pages(f), 1):
            interpreter.process_page(page)
            layout = device.get_result()

            page_text = []
            font_info = []

            for element in layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    if text:
                        page_text.append(text)

                        # 尝试获取字体信息
                        if hasattr(element, 'objs') and element.objs:
                            for obj in element.objs:
                                if hasattr(obj, 'fontname'):
                                    font_info.append({
                                        'font': obj.fontname,
                                        'size': getattr(obj, 'size', 0),
                                        'text': text[:50] if len(text) > 50 else text
                                    })

            pages_data.append({
                'page': page_num,
                'text': '\n'.join(page_text),
                'fonts': font_info
            })

    device.close()
    return pages_data