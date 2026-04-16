"""内容提取器 - 从 PDF 提取页面内容和页码"""
import pypdf
from typing import List, Dict


class ContentExtractor:
    """PDF 内容提取器"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = pypdf.PdfReader(pdf_path)
        self.total_pages = len(self.reader.pages)
        self.content_by_page: List[Dict] = []
        self.pdf_to_actual_page_map: Dict[int, int] = {}
        self.average_chars: float = 0.0

    def extract_all(self) -> List[Dict]:
        """提取所有页面内容"""
        print(f"正在读取 PDF，共 {self.total_pages} 页...")

        for i in range(self.total_pages):
            text = self.reader.pages[i].extract_text()
            actual_page = self._extract_page_number(text, i + 1)

            if text:
                char_count = len(text.strip())
                word_count = len(text.split())
                lines = text.count('\n')

                self.content_by_page.append({
                    'page': i + 1,
                    'actual_page': actual_page,
                    'chars': char_count,
                    'words': word_count,
                    'lines': lines,
                    'text': text
                })
            else:
                self.content_by_page.append({
                    'page': i + 1,
                    'actual_page': actual_page,
                    'chars': 0,
                    'words': 0,
                    'lines': 0,
                    'text': ''
                })

            self.pdf_to_actual_page_map[i + 1] = actual_page

        self.average_chars = (
            sum(c['chars'] for c in self.content_by_page) / len(self.content_by_page)
            if self.content_by_page else 0
        )
        print(f"读取完成，平均每页 {self.average_chars:.1f} 字符\n")
        return self.content_by_page

    def _extract_page_number(self, text: str, fallback_pdf_page: int) -> int:
        """从页面文本中提取实际页码"""
        if not text:
            return fallback_pdf_page

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
