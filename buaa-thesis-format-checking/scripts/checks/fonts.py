"""字体检测 - 使用 PyMuPDF 提取字体信息"""
from typing import List, Dict
import re

# 尝试导入 PyMuPDF
try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


def check_fonts(pdf_path: str, content_by_page: List[Dict], thesis_type: str = "cn") -> Dict:
    """
    使用 PyMuPDF 检测 PDF 字体使用情况
    
    Returns:
        Dict with keys: result, warnings
    """
    result = {
        'fonts_detected': [],
        'font_usage': {},
        'body_fonts': {},
        'heading_fonts': {},
        'font_issues': [],  # 具体的字体问题列表
        'size_issues': [],  # 具体的字号问题列表
        'warnings': [],
        'analyzed_pages': 0
    }

    if not PYMUPDF_AVAILABLE:
        result['warnings'].append(
            "PyMuPDF 未安装，无法检测字体。请运行: pip install pymupdf"
        )
        return {'result': result, 'warnings': result['warnings']}

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        result['warnings'].append(f"无法打开 PDF 文件: {e}")
        return {'result': result, 'warnings': result['warnings']}

    # 分析正文页面 (跳过前5页封面/摘要和后10页参考文献)
    start_page = 5
    end_page = min(len(content_by_page) - 10, len(doc))

    body_fonts = {}
    heading_fonts = {}
    all_fonts = {}
    font_issues = []  # 具体字体问题
    size_issues = []  # 具体字号问题

    # 预期字体
    if thesis_type == "cn":
        expected_body_fonts = ['SimSun', 'Times New Roman', '宋体', 'Times', 'New Roman', 'Simsun']
        expected_heading_fonts = ['SimHei', '黑体', 'Hei', 'Bold', 'SimSun', '宋体', 'Times New Roman']
    else:
        expected_body_fonts = ['Times New Roman', 'Times', 'New Roman', 'SimSun', '宋体']
        expected_heading_fonts = ['Times New Roman', 'Times', 'Bold', 'SimHei', '黑体']

    print(f"\n   使用 PyMuPDF 分析字体，共分析 {end_page - start_page} 页...")

    for page_num in range(start_page, end_page):
        if page_num >= len(doc):
            break

        page = doc[page_num]
        text_dict = page.get_text("dict")

        if "blocks" not in text_dict:
            continue

        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    font_name = span.get("font", "Unknown")
                    font_size = span.get("size", 0)
                    text = span.get("text", "").strip()

                    if not text or len(text) < 2:
                        continue

                    # 过滤掉纯数字、符号、空白
                    if re.match(r'^[\d\s\.\,\:\;\-\+\=\(\)\[\]\{\}]+$', text):
                        continue

                    # 统计字体使用
                    if font_name not in all_fonts:
                        all_fonts[font_name] = {'count': 0, 'sizes': set(), 'pages': set()}
                    all_fonts[font_name]['count'] += len(text)
                    all_fonts[font_name]['sizes'].add(font_size)
                    all_fonts[font_name]['pages'].add(page_num + 1)

                    # 判断是否为标题
                    is_heading = False
                    heading_keywords = ['章', '节', '第', 'chapter', 'section', '参考文献', '致谢', '摘要', 'Abstract']
                    if font_size >= 14:
                        is_heading = True
                    elif any(kw in text[:10] for kw in heading_keywords):
                        is_heading = True

                    if is_heading:
                        if font_name not in heading_fonts:
                            heading_fonts[font_name] = {'count': 0, 'sizes': set()}
                        heading_fonts[font_name]['count'] += len(text)
                        heading_fonts[font_name]['sizes'].add(font_size)
                    else:
                        if font_name not in body_fonts:
                            body_fonts[font_name] = {'count': 0, 'sizes': set()}
                        body_fonts[font_name]['count'] += len(text)
                        body_fonts[font_name]['sizes'].add(font_size)

                        # 检查正文字体是否符合规范
                        if len(text) >= 5:  # 只记录较长的文本片段
                            is_correct_font = any(exp in font_name for exp in expected_body_fonts)
                            if not is_correct_font:
                                font_issues.append({
                                    'page': page_num + 1,
                                    'text': text[:50] + '...' if len(text) > 50 else text,
                                    'font': font_name,
                                    'size': font_size,
                                    'issue': f'正文使用了非规范字体',
                                    'expected': 'SimSun/Times New Roman'
                                })

                        # 检查字号问题
                        if thesis_type == "cn":
                            # 中文论文正文规范字号为5号(10.5pt)或小5号(9pt)
                            if 8 <= font_size <= 12:
                                pass  # 正常范围
                            elif font_size < 8:
                                size_issues.append({
                                    'page': page_num + 1,
                                    'text': text[:50] + '...' if len(text) > 50 else text,
                                    'size': font_size,
                                    'issue': f'字号过小({font_size}pt)',
                                    'expected': '9-10.5pt'
                                })
                            elif font_size > 12 and font_size < 14:
                                size_issues.append({
                                    'page': page_num + 1,
                                    'text': text[:50] + '...' if len(text) > 50 else text,
                                    'size': font_size,
                                    'issue': f'字号偏大({font_size}pt)，可能为非正文内容',
                                    'expected': '9-10.5pt'
                                })

    doc.close()

    result['analyzed_pages'] = end_page - start_page

    # 分析字体问题
    unique_fonts = len(all_fonts)
    result['fonts_detected'] = list(all_fonts.keys())

    if unique_fonts > 5:
        result['warnings'].append(
            f"检测到 {unique_fonts} 种不同字体，论文规范建议正文不超过 2-3 种字体"
        )

    # 检查正文字体
    if body_fonts:
        sorted_body_fonts = sorted(body_fonts.items(), key=lambda x: x[1]['count'], reverse=True)
        main_body_font = sorted_body_fonts[0][0] if sorted_body_fonts else None

        has_issue = True
        for bf in sorted_body_fonts[:3]:
            font_name = bf[0]
            if any(exp in font_name for exp in expected_body_fonts):
                has_issue = False
                break

        if has_issue and main_body_font:
            result['warnings'].append(
                f"正文字体可能不符合规范。主用字体: {main_body_font}，规范要求中文论文正文使用宋体(SimSun)或Times New Roman"
            )

    # 构建字体报告
    result['font_usage'] = {
        font: {
            'count': data['count'],
            'sizes': sorted(list(data['sizes'])),
            'pages': len(data['pages'])
        }
        for font, data in all_fonts.items()
    }
    result['body_fonts'] = {
        font: {'count': data['count'], 'sizes': sorted(list(data['sizes']))}
        for font, data in body_fonts.items()
    }
    result['heading_fonts'] = {
        font: {'count': data['count'], 'sizes': sorted(list(data['sizes']))}
        for font, data in heading_fonts.items()
    }
    
    # 限制问题数量，避免报告过长
    result['font_issues'] = font_issues[:20]
    result['size_issues'] = size_issues[:20]

    # 打印字体汇总
    print(f"   检测到 {unique_fonts} 种字体:")
    for font, data in sorted(all_fonts.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
        sizes_str = ", ".join(f"{s:.1f}pt" for s in sorted(list(data['sizes']))[:3])
        print(f"     - {font}: {data['count']} 字符, 字号 {sizes_str}, {len(data['pages'])} 页")

    if font_issues:
        print(f"   ⚠️  发现 {len(font_issues)} 处正文字体问题 (显示前20处):")
        for iss in font_issues[:5]:
            print(f"     - 第{iss['page']}页: 「{iss['text']}」使用 {iss['font']} ({iss['size']:.1f}pt)")

    if size_issues:
        print(f"   ⚠️  发现 {len(size_issues)} 处字号问题 (显示前20处):")
        for iss in size_issues[:5]:
            print(f"     - 第{iss['page']}页: 「{iss['text']}」字号 {iss['size']:.1f}pt")

    if len(all_fonts) > 10:
        print(f"     ... 还有 {len(all_fonts) - 10} 种字体")

    return {'result': result, 'warnings': result['warnings']}
