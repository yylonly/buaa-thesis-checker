"""字体与行间距检测 - 含详细间距问题表"""
import re
from typing import List, Dict


def check_font_and_spacing(content_by_page: List[Dict], thesis_type: str = "cn") -> Dict:
    """
    检测字体使用和行间距情况

    Returns:
        Dict with keys: result, warnings
    """
    result = {
        'fonts_detected': [],
        'line_spacing_issues': [],
        'spacing_type': 'unknown',  # single, 1.5, double
        'analyzed_pages': 0,
        'spacing_issues_table': [],  # 详细间距问题表
    }

    warnings = []
    spacing_info = []
    spacing_issues = []  # 收集各类间距问题

    # 分析正文页面 (跳过前5页和后10页)
    body_pages = content_by_page[5:min(50, len(content_by_page) - 10)]

    for content in body_pages:
        if not content['text'] or content['chars'] < 200:
            continue

        lines = content['text'].split('\n')
        if len(lines) < 5:
            continue

        # 计算行间距特征
        blank_lines = sum(1 for line in lines if len(line.strip()) == 0)
        total_lines = len(lines)
        non_empty_lines = total_lines - blank_lines

        if non_empty_lines > 0:
            blank_ratio = blank_lines / non_empty_lines
            line_height_estimate = total_lines / max(non_empty_lines, 1)

            spacing_info.append({
                'page': content['page'],
                'total_lines': total_lines,
                'non_empty_lines': non_empty_lines,
                'blank_lines': blank_lines,
                'blank_ratio': round(blank_ratio, 3),
                'line_height_estimate': round(line_height_estimate, 2),
                'chars': content['chars']
            })

    # 分析行间距模式
    if spacing_info:
        avg_blank_ratio = sum(s['blank_ratio'] for s in spacing_info) / len(spacing_info)
        avg_line_height = sum(s['line_height_estimate'] for s in spacing_info) / len(spacing_info)

        # 根据空白行比例和行高估算间距类型
        if avg_blank_ratio < 0.15 and avg_line_height < 1.3:
            result['spacing_type'] = "单倍行距 / Single Spacing"
            print(f"\n   行间距分析: 检测为单倍行距 (blank_ratio={avg_blank_ratio:.2f}, line_height={avg_line_height:.2f})")
        elif avg_blank_ratio < 0.4 and avg_line_height < 1.6:
            result['spacing_type'] = "1.5倍行距 / 1.5 Line Spacing"
            print(f"\n   行间距分析: 检测为1.5倍行距 (blank_ratio={avg_blank_ratio:.2f}, line_height={avg_line_height:.2f})")
        else:
            result['spacing_type'] = "双倍行距或更大 / Double Spacing or More"
            print(f"\n   行间距分析: 检测为双倍行距或更大 (blank_ratio={avg_blank_ratio:.2f}, line_height={avg_line_height:.2f})")

        # 检查不正常的间距页面
        irregular_pages = []
        for s in spacing_info:
            if abs(s['blank_ratio'] - avg_blank_ratio) > 0.3:
                irregular_pages.append(s['page'])

        if irregular_pages:
            spacing_issues.append({
                'category': '行间距一致性',
                'issue': f'{len(irregular_pages)}页行间距异常',
                'pages': irregular_pages[:5],
                'severity': 'warning'
            })

        result['analyzed_pages'] = len(spacing_info)

    # 中文论文规范要求：正文应使用1.5倍行距或固定行距
    if thesis_type == "cn":
        if result['spacing_type'] == "单倍行距 / Single Spacing":
            spacing_issues.append({
                'category': '正文行距',
                'issue': '正文使用单倍行距',
                'requirement': '规范要求1.5倍行距',
                'severity': 'error'
            })
            warnings.append(
                f"检测到正文使用单倍行距，规范要求中文论文正文应使用1.5倍行距 / Detected single line spacing; Chinese thesis standard requires 1.5 line spacing"
            )
            print(f"   ⚠️  规范要求中文论文正文使用1.5倍行距")
        elif result['spacing_type'] == "双倍行距或更大 / Double Spacing or More":
            spacing_issues.append({
                'category': '正文行距',
                'issue': '正文使用双倍行距或更大',
                'requirement': '规范要求1.5倍行距',
                'severity': 'error'
            })
            warnings.append(
                f"检测到正文使用双倍行距或更大，规范要求中文论文正文应使用1.5倍行距 / Detected double or larger line spacing; Chinese thesis standard requires 1.5 line spacing"
            )
            print(f"   ⚠️  规范要求中文论文正文使用1.5倍行距")
        else:
            print(f"   ✅ 行间距符合中文论文规范要求 (1.5倍行距)")
    else:
        # 英文论文通常使用单倍行距或1.5倍行距
        if result['spacing_type'] == "双倍行距或更大 / Double Spacing or More":
            spacing_issues.append({
                'category': '正文行距',
                'issue': '正文使用双倍行距或更大',
                'requirement': '推荐使用单倍或1.5倍行距',
                'severity': 'warning'
            })
            warnings.append(
                f"检测到正文使用双倍行距，英文论文推荐使用单倍或1.5倍行距 / Detected double or larger line spacing; English thesis recommended to use single or 1.5 line spacing"
            )
        else:
            print(f"   ✅ 行间距符合英文论文推荐规范")

    # 字体检测 - pypdf无法直接获取字体信息，做提示性输出
    print(f"\n   字体信息: pypdf无法直接提取字体详情，请使用专业PDF工具检查字体使用规范")
    print(f"   建议检查: 正文字体应为宋体(中文)或Times New Roman(英文)，标题字体应与正文不同")

    result['line_spacing_issues'] = spacing_info
    result['spacing_issues_table'] = spacing_issues

    return {
        'result': result,
        'warnings': warnings
    }


def analyze_detailed_spacing(pdf_path: str, content_by_page: List[Dict], thesis_type: str = "cn") -> Dict:
    """
    使用 PyMuPDF 分析详细间距问题（图表、公式与正文间距等）

    Returns:
        Dict with detailed spacing issues
    """
    try:
        import pymupdf
    except ImportError:
        return {'warnings': ['PyMuPDF 未安装，无法检测详细间距问题']}

    result = {
        'spacing_issues_table': [],
        'figure_spacing_issues': [],
        'table_spacing_issues': [],
        'formula_spacing_issues': [],
        'warnings': []
    }

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        result['warnings'].append(f"无法打开PDF: {e}")
        return result

    # 分析页面布局
    start_page = 5
    end_page = min(len(content_by_page) - 10, len(doc))

    print(f"\n   使用 PyMuPDF 分析详细间距，共分析 {end_page - start_page} 页...")

    # 各类间距问题收集
    spacing_issues = []

    for page_num in range(start_page, end_page):
        if page_num >= len(doc):
            break

        page = doc[page_num]
        text_dict = page.get_text("dict")

        if "blocks" not in text_dict:
            continue

        # 收集所有文本块信息
        text_blocks = []
        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    if text:
                        bbox = span.get("bbox", {})
                        # PyMuPDF bbox can be tuple (x0, y0, x1, y1) or dict
                        if isinstance(bbox, tuple):
                            y0, y1 = bbox[1], bbox[3]
                        else:
                            y0 = bbox.get('y0', 0)
                            y1 = bbox.get('y1', 0)
                        text_blocks.append({
                            'text': text,
                            'bbox': bbox,
                            'y0': y0,
                            'y1': y1,
                            'font_size': span.get('size', 0)
                        })

        # 检测图表标题（通过关键词和位置关系）
        page_text = page.get_text("text")
        lines = page_text.split('\n')

        # 图序/表序/公式序 检测
        figure_pattern = r'图\s*\d+'
        table_pattern = r'表\s*\d+'
        formula_pattern = r'\(\d+\.\d+\)'

        has_figure = bool(re.search(figure_pattern, page_text))
        has_table = bool(re.search(table_pattern, page_text))
        has_formula = bool(re.search(formula_pattern, page_text))

        # 检测图表与上下文间距问题（通过空白行分析）
        if has_figure:
            # 统计图表附近的空白行比例
            fig_blocks = [b for b in text_blocks if '图' in b['text'] or re.search(figure_pattern, b['text'])]
            if fig_blocks:
                # 检查图表前后是否有足够间距
                for fb in fig_blocks:
                    # 简单检查：如果图表前后空白行太少
                    nearby = [b for b in text_blocks
                             if abs(b['y0'] - fb['y0']) < 50 or abs(b['y1'] - fb['y1']) < 50]
                    if len(nearby) > 0:
                        # 检查是否有明确间距
                        y_positions = sorted([b['y0'] for b in nearby])
                        gaps = [y_positions[i+1] - y_positions[i] for i in range(len(y_positions)-1)]
                        if gaps and max(gaps) < 10:  # 间距太小
                            spacing_issues.append({
                                'category': '图表与正文间距',
                                'page': page_num + 1,
                                'issue': f'图附近间距可能不足',
                                'severity': 'warning'
                            })
                            break

        if has_table:
            tbl_blocks = [b for b in text_blocks if '表' in b['text'] or re.search(table_pattern, b['text'])]
            if tbl_blocks:
                for tb in tbl_blocks:
                    nearby = [b for b in text_blocks
                             if abs(b['y0'] - tb['y0']) < 50 or abs(b['y1'] - tb['y1']) < 50]
                    if len(nearby) > 0:
                        y_positions = sorted([b['y0'] for b in nearby])
                        gaps = [y_positions[i+1] - y_positions[i] for i in range(len(y_positions)-1)]
                        if gaps and max(gaps) < 10:
                            spacing_issues.append({
                                'category': '表格与正文间距',
                                'page': page_num + 1,
                                'issue': f'表附近间距可能不足',
                                'severity': 'warning'
                            })
                            break

        if has_formula:
            frm_blocks = [b for b in text_blocks if re.search(formula_pattern, b['text'])]
            if frm_blocks:
                for frb in frm_blocks:
                    nearby = [b for b in text_blocks
                             if abs(b['y0'] - frb['y0']) < 30 or abs(b['y1'] - frb['y1']) < 30]
                    if len(nearby) > 0:
                        y_positions = sorted([b['y0'] for b in nearby])
                        gaps = [y_positions[i+1] - y_positions[i] for i in range(len(y_positions)-1)]
                        if gaps and max(gaps) < 8:
                            spacing_issues.append({
                                'category': '公式间距',
                                'page': page_num + 1,
                                'issue': f'公式附近间距可能不足',
                                'severity': 'warning'
                            })
                            break

    doc.close()

    # 去重
    unique_issues = []
    seen = set()
    for issue in spacing_issues:
        key = (issue['category'], issue.get('page', 0))
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    result['spacing_issues_table'] = unique_issues

    # 打印汇总
    if unique_issues:
        print(f"   发现 {len(unique_issues)} 处间距问题:")
        for iss in unique_issues[:5]:
            print(f"     - [{iss['category']}] 第{iss.get('page', '?')}页: {iss['issue']}")

    return result