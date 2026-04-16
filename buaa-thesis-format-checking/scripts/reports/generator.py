"""报告生成器 - HTML 报告"""
import os
from typing import Dict, List


def generate_html_report(
    pdf_path: str,
    total_pages: int,
    average_chars: float,
    issues: List[str],
    bottom_blank_pages: List[Dict],
    alignment_issues: List[Dict],
    missing_transitions: List[Dict] = [],
    spacing_info: Dict = {},
    font_info: Dict = {},
    detailed_spacing_info: Dict = {},
    output_dir: str = "."
) -> str:
    """生成 HTML 格式的完整检测报告"""
    from datetime import datetime as dt

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.join(output_dir, f"{pdf_name}_audit_report_{timestamp}.html")

    # Merge all issues (warnings are now treated as issues)
    all_issues = issues
    total_issues = len(all_issues)

    # Issues rows - split by " / " for bilingual display
    issues_rows = ""
    if all_issues:
        for issue in all_issues:
            if " / " in issue:
                parts = issue.split(" / ", 1)
                zh = parts[0].strip()
                en = parts[1].strip()
            else:
                zh = issue.strip()
                en = issue.strip()
            issues_rows += f"    <tr><td class='zh-text'>{zh}</td><td class='en-text'>{en}</td></tr>\n"
    else:
        issues_rows = "    <tr><td colspan='2'>✅ 无问题项</td></tr>\n"

    # Bottom blank rows
    blank_rows = ""
    if bottom_blank_pages:
        for bp in bottom_blank_pages:
            blank_rows += f"    <tr><td>{bp['page']}</td><td>{bp.get('position', '')}</td><td>{bp.get('content_before_blank', '')}</td></tr>\n"
    else:
        blank_rows = "    <tr><td colspan='3'>✅ 无</td></tr>\n"

    # Alignment issues rows
    alignment_rows = ""
    if alignment_issues:
        for ai in alignment_issues:
            alignment_rows += f"    <tr><td>{ai['page']}</td><td>{ai.get('type', '')}</td><td>{ai.get('detail', '')}</td></tr>\n"
    else:
        alignment_rows = "    <tr><td colspan='3'>✅ 无</td></tr>\n"

    # Missing transitions table rows
    transition_rows = ""
    if missing_transitions:
        for mt in missing_transitions:
            transition_rows += f"    <tr><td>{mt['page']}</td><td>{mt.get('parent_level2', '')}</td><td>{mt.get('title', '')}</td></tr>\n"
    else:
        transition_rows = "    <tr><td colspan='3'>✅ 无</td></tr>\n"

    # Font and line spacing info
    spacing_type = spacing_info.get('spacing_type', '未知 / Unknown')
    spacing_pages = spacing_info.get('analyzed_pages', 0)
    spacing_summary = f"检测结果 / Detected: {spacing_type} | 分析页数 / Analyzed Pages: {spacing_pages}"

    # Font info section
    fonts_detected = font_info.get('fonts_detected', [])
    font_usage = font_info.get('font_usage', {})
    unique_fonts = len(fonts_detected)
    font_issues = font_info.get('font_issues', [])
    size_issues = font_info.get('size_issues', [])

    if unique_fonts > 0:
        font_summary = f"检测到 {unique_fonts} 种字体 (共分析 {font_info.get('analyzed_pages', 0)} 页)"
        font_details = ""
        for font, data in sorted(font_usage.items(), key=lambda x: x[1]['count'], reverse=True)[:8]:
            sizes_str = ", ".join(f"{s:.1f}pt" for s in data.get('sizes', [])[:3])
            font_details += f"      <tr><td>{font}</td><td>{data['count']}</td><td>{sizes_str}</td><td>{data.get('pages', 0)}</td></tr>\n"
    else:
        font_summary = "未检测到字体信息"
        font_details = ""

    # 具体字体问题表
    font_issues_html = ""
    if font_issues:
        font_issues_rows = ""
        for iss in font_issues[:20]:
            font_issues_rows += f"      <tr class='error'><td>{iss.get('page', '-')}</td><td style='max-width: 300px; overflow: hidden; text-overflow: ellipsis;'>{iss.get('text', '')}</td><td>{iss.get('font', '')}</td><td>{iss.get('size', 0):.1f}pt</td><td>{iss.get('expected', '-')}</td></tr>\n"
        font_issues_html = f"""
  <h3>字体问题详情 / Font Issues Detail</h3>
  <table>
    <tr><th>页码</th><th>问题文字</th><th>当前字体</th><th>字号</th><th>规范字体</th></tr>
{font_issues_rows}  </table>
"""
    else:
        font_issues_html = ""

    # 具体字号问题表
    size_issues_html = ""
    if size_issues:
        size_issues_rows = ""
        for iss in size_issues[:20]:
            size_issues_rows += f"      <tr class='warning'><td>{iss.get('page', '-')}</td><td style='max-width: 300px; overflow: hidden; text-overflow: ellipsis;'>{iss.get('text', '')}</td><td>{iss.get('size', 0):.1f}pt</td><td>{iss.get('expected', '-')}</td><td>{iss.get('issue', '')}</td></tr>\n"
        size_issues_html = f"""
  <h3>字号问题详情 / Font Size Issues Detail</h3>
  <table>
    <tr><th>页码</th><th>问题文字</th><th>当前字号</th><th>规范字号</th><th>问题描述</th></tr>
{size_issues_rows}  </table>
"""
    else:
        size_issues_html = ""

    # Build font section HTML
    if unique_fonts > 0:
        font_section_html = f"""
  <p style="margin: 10px 0; color: #666; font-size: 13px;">{font_summary}</p>
  <table style="margin-top: 10px;">
    <tr><th>字体 Font</th><th>字符数 Characters</th><th>字号 Sizes</th><th>页数 Pages</th></tr>
{font_details}  </table>
{font_issues_html}
{size_issues_html}
  <div class="standards" style="margin-top: 10px;">
    <strong>规范要求 / Requirements:</strong> 中文论文正文应为宋体(SimSun)或Times New Roman，标题字体应与正文不同；正文字号应为9-10.5pt(小五号至五号)
  </div>
"""
    else:
        font_section_html = f"""
  <p style="margin: 10px 0; color: #888; font-size: 12px;">{font_summary}</p>
  <p style="margin: 10px 0; color: #888; font-size: 12px;">请安装 PyMuPDF: pip install pymupdf</p>
"""

    # 详细间距问题表
    spacing_issues_table = detailed_spacing_info.get('spacing_issues_table', [])
    if spacing_issues_table:
        spacing_table_rows = ""
        for iss in spacing_issues_table:
            if not isinstance(iss, dict):
                continue
            severity_class = 'error' if iss.get('severity') == 'error' else 'warning'
            severity_text = '❌' if severity_class == 'error' else '⚠️'
            # 处理 pages 字段（有些issue用pages有些用page）
            page_or_pages = iss.get('page', iss.get('pages', '-'))
            if isinstance(page_or_pages, list):
                page_or_pages = ', '.join(str(p) for p in page_or_pages)
            spacing_table_rows += f"      <tr class='{severity_class}'><td>{iss.get('category', '')}</td><td>{page_or_pages}</td><td>{iss.get('issue', '')}</td><td>{iss.get('requirement', '-')}</td><td>{severity_text} {iss.get('severity', '')}</td></tr>\n"
        spacing_issues_html = f"""
  <h3>间距问题详情 / Spacing Issues Detail</h3>
  <table>
    <tr><th>问题类别 Category</th><th>页码 Page</th><th>问题描述 Issue</th><th>规范要求 Requirement</th><th>严重程度 Severity</th></tr>
{spacing_table_rows}  </table>
"""
    else:
        spacing_issues_html = """
  <p style="margin: 10px 0; color: #888;">未检测到详细间距问题</p>
"""

    # 间距规范参考表
    spacing_standards_html = """
  <div class="standards" style="margin-top: 15px;">
    <h4 style="margin: 0 0 10px;">规范参考 / Standards Reference</h4>
    <table style="font-size: 12px;">
      <tr><th style="width: 30%;">类别</th><th style="width: 35%;">中文论文要求</th><th style="width: 35%;">English Requirements</th></tr>
      <tr><td><b>正文行距</b></td><td>1.5倍行距，段前段后无空行</td><td>1.5-line spacing, no blank lines before/after paragraph</td></tr>
      <tr><td><b>标题行距</b></td><td>单倍行距，段前段后各0.5行</td><td>Single spacing, 0.5 line before and after</td></tr>
      <tr><td><b>图与正文间距</b></td><td>段前6磅，段后12磅</td><td>6pt before, 12pt after</td></tr>
      <tr><td><b>表与正文间距</b></td><td>段前12磅，段后6磅</td><td>12pt before, 6pt after</td></tr>
      <tr><td><b>公式间距</b></td><td>按章编排，编号在右边行末</td><td>Numbered by chapter, label at right end of line</td></tr>
    </table>
  </div>
"""

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>论文格式检测报告</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #333;
    max-width: 960px;
    margin: 0 auto;
    padding: 20px;
    background: #f5f5f5;
  }}
  .header {{
    background: linear-gradient(135deg, #1a5276, #2980b9);
    color: white;
    padding: 30px;
    border-radius: 10px 10px 0 0;
    text-align: center;
  }}
  .header h1 {{ margin: 0 0 8px; font-size: 24px; }}
  .header p {{ margin: 0; opacity: 0.9; font-size: 13px; }}
  .summary {{
    background: white;
    padding: 20px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    border-bottom: 1px solid #eee;
  }}
  .stat {{
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    background: #f8f9fa;
  }}
  .stat-value {{ font-size: 28px; font-weight: bold; }}
  .stat-label {{ font-size: 12px; color: #888; margin-top: 4px; }}
  .stat.issues .stat-value {{ color: #c62828; }}
  .section {{
    background: white;
    margin: 10px 0;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }}
  .section h2 {{
    color: #1a5276;
    border-bottom: 2px solid #2980b9;
    padding-bottom: 10px;
    margin-top: 0;
    font-size: 16px;
  }}
  .section h3 {{ color: #1a5276; font-size: 14px; margin: 15px 0 10px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
  }}
  th {{ background: #f8f9fa; font-weight: bold; color: #1a5276; }}
  tr:hover {{ background: #fafafa; }}
  tr.error {{ background: #ffebee; }}
  tr.warning {{ background: #fff8e1; }}
  .zh-text {{ color: #c62828; }}
  .en-text {{ color: #555; font-style: italic; }}
  .footer {{
    text-align: center;
    padding: 20px;
    color: #888;
    font-size: 12px;
  }}
  .standards {{
    background: #f8f9fa;
    padding: 15px 20px;
    border-radius: 5px;
    margin-top: 10px;
    font-size: 13px;
    color: #666;
  }}
  .standards h4 {{ margin: 0 0 10px; color: #1a5276; }}
</style>
</head>
<body>

<div class="header">
  <h1>论文格式检测报告</h1>
  <p>BUAA Master's Thesis Format Audit Report</p>
</div>

<div class="summary">
  <div class="stat">
    <div class="stat-value">{total_pages}</div>
    <div class="stat-label">总页数</div>
  </div>
  <div class="stat">
    <div class="stat-value">{average_chars:.0f}</div>
    <div class="stat-label">平均字符/页</div>
  </div>
  <div class="stat issues">
    <div class="stat-value">{total_issues}</div>
    <div class="stat-label">问题项</div>
  </div>
</div>

<div class="section">
  <h2>❌ 问题项 / Issues</h2>
  <table>
    <tr><th>中文描述</th><th>英文描述</th></tr>
{issues_rows}  </table>
</div>

<div class="section">
  <h2>文本对齐问题 / Alignment Issues</h2>
  <table>
    <tr><th>页码 Page</th><th>类型 Type</th><th>详情 Detail</th></tr>
{alignment_rows}  </table>
</div>

<div class="section">
  <h2>页面中包含大量空白行 / Page with Many Empty Rows</h2>
  <table>
    <tr><th>页码 Page</th><th>空白位置 Position</th><th>空白前最后内容 Last Content Before Blank</th></tr>
{blank_rows}  </table>
</div>

<div class="section">
  <h2>缺少过渡段的章节 / Sections Missing Transition Paragraphs</h2>
  <table>
    <tr><th>页码 Page</th><th>二级标题 Level-2 Heading</th><th>三级标题 Level-3 Heading</th></tr>
{transition_rows}  </table>
</div>

<div class="section">
  <h2>字体与行间距 / Font & Line Spacing</h2>
  <p style="margin: 10px 0; color: #666; font-size: 13px;">{spacing_summary}</p>
  {font_section_html}
  {spacing_issues_html}
  {spacing_standards_html}
</div>

<div class="standards">
  <strong>依据标准 / Standards:</strong> 《北京航空航天大学学位论文书写规范与排版格式》
</div>

<div class="footer">
  <p>报告生成时间: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>

</body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"🌐 HTML报告已保存: {html_path}")
    return html_path