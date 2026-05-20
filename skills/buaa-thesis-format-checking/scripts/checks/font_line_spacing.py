"""字体与行间距检测 - 使用 PyMuPDF 精确分析视觉行距"""
import re
from typing import List, Dict

# 尝试导入 PyMuPDF
try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


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
        'spacing_issues_table': [],
    }

    warnings = []
    spacing_info = []
    spacing_issues = []

    # 使用 PyMuPDF 进行精确的行间距分析
    if PYMUPDF_AVAILABLE:
        # 通过 content_by_page 获取 pdf_path
        pdf_path = None
        for content in content_by_page:
            if 'pdf_path' in content:
                pdf_path = content.get('pdf_path')
                break

        if pdf_path:
            spacing_result = analyze_line_spacing_with_pymupdf(
                pdf_path,
                content_by_page,
                thesis_type
            )
            result.update(spacing_result)
            warnings.extend(spacing_result.get('warnings', []))
            return {'result': result, 'warnings': warnings}

    # 如果 PyMuPDF 不可用，使用基于文本的启发式分析（不准确，仅作为后备）
    result['spacing_type'] = 'unknown (PyMuPDF not available)'
    result['warnings'] = ['PyMuPDF 未安装，行间距检测不准确。请运行: pip install pymupdf']
    warnings.append('PyMuPDF 未安装，无法准确检测行间距')

    return {
        'result': result,
        'warnings': warnings
    }


def analyze_line_spacing_with_pymupdf(pdf_path: str, content_by_page: List[Dict], thesis_type: str = "cn") -> Dict:
    """
    使用 PyMuPDF 精确分析行间距

    Returns:
        Dict with spacing analysis results
    """
    result = {
        'spacing_type': 'unknown',
        'spacing_ratio': 0.0,
        'analyzed_pages': 0,
        'page_spacing_details': [],
        'warnings': [],
        'spacing_issues_table': []
    }

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        result['warnings'].append(f"无法打开PDF文件: {e}")
        return result

    # 分析正文页面 (跳过前5页封面/摘要和后10页参考文献)
    start_page = 5
    end_page = min(len(content_by_page) - 10, len(doc))

    page_spacing_data = []
    spacing_ratios = []

    print(f"\n   使用 PyMuPDF 分析行间距，共分析 {end_page - start_page} 页...")

    for page_num in range(start_page, end_page):
        if page_num >= len(doc):
            break

        page = doc[page_num]
        text_dict = page.get_text("dict")

        if "blocks" not in text_dict:
            continue

        # 收集所有文本行的y坐标
        line_y_positions = []
        line_heights = []

        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                bbox = line.get("bbox", {})
                if isinstance(bbox, tuple) and len(bbox) >= 4:
                    y0 = bbox[1]
                    y1 = bbox[3]
                    line_heights.append(y1 - y0)
                    line_y_positions.append(y0)

        if len(line_y_positions) < 5:
            continue

        # 计算相邻行之间的间距
        sorted_y = sorted(line_y_positions)
        if len(sorted_y) > 1:
            spacings = [sorted_y[i + 1] - sorted_y[i] for i in range(len(sorted_y) - 1)]
            # 过滤掉异常值（表格线、图表元素等），正常中文正文行距在14-30pt之间
            valid_spacings = [s for s in spacings if 14 < s < 35]
            if valid_spacings:
                avg_spacing = sum(valid_spacings) / len(valid_spacings)
                avg_line_height = sum(line_heights) / len(line_heights) if line_heights else 12
                # 正确的计算：行距倍数 = 实际行间距 / 字体大小
                # avg_spacing 是从一行顶部到下一行顶部的距离（即一个line box的高度）
                # 但这包含了 font size + leading，所以直接除以 font size
                spacing_ratio = avg_spacing / avg_line_height if avg_line_height > 0 else 1.0

                page_spacing_data.append({
                    'page': page_num + 1,
                    'avg_spacing': avg_spacing,
                    'avg_line_height': avg_line_height,
                    'spacing_ratio': spacing_ratio,
                    'line_count': len(sorted_y)
                })
                spacing_ratios.append(spacing_ratio)

    doc.close()

    if spacing_ratios:
        overall_ratio = sum(spacing_ratios) / len(spacing_ratios)
        result['analyzed_pages'] = len(page_spacing_data)
        result['spacing_ratio'] = round(overall_ratio, 2)
        result['page_spacing_details'] = page_spacing_data[:10]

        # 判断行距类型
        if overall_ratio < 1.25:
            result['spacing_type'] = "单倍行距 / Single Spacing"
        elif overall_ratio < 1.65:
            result['spacing_type'] = "1.5倍行距 / 1.5 Line Spacing"
        else:
            result['spacing_type'] = "双倍行距或更大 / Double Spacing or More"

        # 打印分析结果
        print(f"\n   行间距分析结果:")
        print(f"   - 分析页数: {len(page_spacing_data)}")
        print(f"   - 平均行距倍数: {overall_ratio:.2f}x")
        print(f"   - 行距类型: {result['spacing_type']}")

        # 中文论文规范检查
        if thesis_type == "cn":
            if overall_ratio < 1.25:
                result['warnings'].append(
                    f"检测到正文使用单倍行距({overall_ratio:.2f}x)，规范要求中文论文正文应使用1.5倍行距"
                )
                print(f"   规范要求中文论文正文使用1.5倍行距")
            elif 1.35 <= overall_ratio <= 1.65:
                print(f"   符合中文论文规范要求 (1.5倍行距)")
            else:
                print(f"   行距为 {overall_ratio:.2f}x，规范要求1.5倍行距")

    return result


def analyze_detailed_spacing(pdf_path: str, content_by_page: List[Dict], thesis_type: str = "cn") -> Dict:
    """
    分析图表、公式与正文的间距问题

    Returns:
        Dict with detailed spacing issues
    """
    result = {
        'spacing_issues_table': [],
        'figure_spacing_issues': [],
        'table_spacing_issues': [],
        'formula_spacing_issues': [],
        'warnings': []
    }

    if not PYMUPDF_AVAILABLE:
        result['warnings'].append('PyMuPDF 未安装，无法检测详细间距问题')
        return result

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        result['warnings'].append(f"无法打开PDF: {e}")
        return result

    start_page = 5
    end_page = min(len(content_by_page) - 10, len(doc))

    print(f"\n   使用 PyMuPDF 分析详细间距，共分析 {end_page - start_page} 页...")

    spacing_issues = []

    for page_num in range(start_page, end_page):
        if page_num >= len(doc):
            break

        page = doc[page_num]
        text_dict = page.get_text("dict")

        if "blocks" not in text_dict:
            continue

        text_blocks = []
        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    if text:
                        bbox = span.get("bbox", {})
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

        figure_pattern = r'图\s*\d+'
        table_pattern = r'表\s*\d+'
        formula_pattern = r'\(\d+\.\d+\)'

        page_text = page.get_text("text")
        has_figure = bool(re.search(figure_pattern, page_text))
        has_table = bool(re.search(table_pattern, page_text))
        has_formula = bool(re.search(formula_pattern, page_text))

        if has_figure:
            fig_blocks = [b for b in text_blocks if '图' in b['text'] or re.search(figure_pattern, b['text'])]
            if fig_blocks:
                for fb in fig_blocks:
                    # 找表格前后的内容
                    before = [b for b in text_blocks if b['y0'] < fb['y0'] - 10]
                    after = [b for b in text_blocks if b['y0'] > fb['y1'] + 10]

                    # 检查表格前间距（上一个内容块与表格的距离）
                    if before:
                        last_before = max(before, key=lambda b: b['y1'])
                        gap_before = fb['y0'] - last_before['y1']
                        if gap_before > 0 and gap_before < 15:
                            spacing_issues.append({
                                'category': '图表与正文间距',
                                'page': page_num + 1,
                                'issue': f'图表前间距不足({gap_before:.0f}pt)',
                                'severity': 'warning'
                            })

                    # 检查表格后间距（表格与下一个内容块的距离）
                    if after:
                        first_after = min(after, key=lambda b: b['y0'])
                        gap_after = first_after['y0'] - fb['y1']
                        if gap_after > 0 and gap_after < 15:
                            spacing_issues.append({
                                'category': '图表与正文间距',
                                'page': page_num + 1,
                                'issue': f'图表后间距不足({gap_after:.0f}pt)',
                                'severity': 'warning'
                            })

        if has_table:
            tbl_blocks = [b for b in text_blocks if '表' in b['text'] or re.search(table_pattern, b['text'])]
            if tbl_blocks:
                for tb in tbl_blocks:
                    # 找表格前后的内容
                    before = [b for b in text_blocks if b['y0'] < tb['y0'] - 10]
                    after = [b for b in text_blocks if b['y0'] > tb['y1'] + 10]

                    # 检查表格前间距
                    if before:
                        last_before = max(before, key=lambda b: b['y1'])
                        gap_before = tb['y0'] - last_before['y1']
                        if gap_before > 0 and gap_before < 15:
                            spacing_issues.append({
                                'category': '表格与正文间距',
                                'page': page_num + 1,
                                'issue': f'表格前间距不足({gap_before:.0f}pt)',
                                'severity': 'warning'
                            })

                    # 检查表格后间距
                    if after:
                        first_after = min(after, key=lambda b: b['y0'])
                        gap_after = first_after['y0'] - tb['y1']
                        if gap_after > 0 and gap_after < 15:
                            spacing_issues.append({
                                'category': '表格与正文间距',
                                'page': page_num + 1,
                                'issue': f'表格后间距不足({gap_after:.0f}pt)',
                                'severity': 'warning'
                            })

        if has_formula:
            frm_blocks = [b for b in text_blocks if re.search(formula_pattern, b['text'])]
            if frm_blocks:
                for frb in frm_blocks:
                    before = [b for b in text_blocks if b['y0'] < frb['y0'] - 10]
                    after = [b for b in text_blocks if b['y0'] > frb['y1'] + 10]

                    if before:
                        last_before = max(before, key=lambda b: b['y1'])
                        gap_before = frb['y0'] - last_before['y1']
                        if gap_before > 0 and gap_before < 12:
                            spacing_issues.append({
                                'category': '公式间距',
                                'page': page_num + 1,
                                'issue': f'公式前间距不足({gap_before:.0f}pt)',
                                'severity': 'warning'
                            })

                    if after:
                        first_after = min(after, key=lambda b: b['y0'])
                        gap_after = first_after['y0'] - frb['y1']
                        if gap_after > 0 and gap_after < 12:
                            spacing_issues.append({
                                'category': '公式间距',
                                'page': page_num + 1,
                                'issue': f'公式后间距不足({gap_after:.0f}pt)',
                                'severity': 'warning'
                            })

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

    if unique_issues:
        print(f"   发现 {len(unique_issues)} 处间距问题:")
        for iss in unique_issues[:5]:
            print(f"     - [{iss['category']}] 第{iss.get('page', '?')}页: {iss['issue']}")

    return result
