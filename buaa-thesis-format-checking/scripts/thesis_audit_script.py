#!/usr/bin/env python3
"""
北京航空航天大学硕士学位论文格式检测脚本
BUAA Master's Thesis Format Audit Script

使用方法:
    python3 thesis_audit_script.py <pdf_path>
    python3 thesis_audit_script.py /path/to/thesis.pdf [output_dir] [--type cn|en]
"""

import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractors.content import ContentExtractor
from checks import (
    check_blank_pages,
    check_placeholders,
    check_section_continuity,
    check_low_content_pages,
    check_incomplete_content,
    check_urls_in_body,
    check_arxiv_without_doi,
    check_abstracts,
    check_text_alignment,
    check_figure_pages,
    check_transition_paragraphs,
    check_font_and_spacing,
    check_fonts,
)
from checks.font_line_spacing import analyze_detailed_spacing
from reports.generator import generate_html_report


def run_full_audit(pdf_path: str, thesis_type: str = "cn", output_dir: str = ".") -> dict:
    """运行完整审计并生成报告"""

    # 1. 提取内容
    print("\n" + "=" * 60)
    print("开始论文格式审计")
    print("=" * 60)

    extractor = ContentExtractor(pdf_path)
    content_by_page = extractor.extract_all()
    total_pages = extractor.total_pages
    average_chars = extractor.average_chars

    # 收集结果
    all_issues = []
    all_warnings = []
    section_info = {}
    bottom_blank_pages = []
    alignment_issues = []

    # 2. 执行各项检测
    print("\n" + "=" * 60)
    print("执行各项检测...")
    print("=" * 60)

    # 2.1 空白页面
    result = check_blank_pages(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.2 占位符
    result = check_placeholders(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.3 章节连续性
    result = check_section_continuity(content_by_page)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))
    section_info = {
        'sections': result.get('sections', []),
        'chapter_pages': result.get('chapter_pages', {}),
        'missing_chapters': result.get('missing_chapters', [])
    }

    # 2.4 低内容页面
    result = check_low_content_pages(content_by_page, average_chars)
    all_warnings.extend(result.get('warnings', []))
    bottom_blank_pages = result.get('bottom_blank_pages', [])

    # 2.5 未完成标记
    result = check_incomplete_content(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.6 过渡段
    result = check_transition_paragraphs(content_by_page)
    all_warnings.extend(result.get('warnings', []))
    missing_transitions = result.get('result', {}).get('missing_transitions', [])

    # 2.7 URL 位置
    result = check_urls_in_body(content_by_page, total_pages)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))

    # 2.8 arXiv DOI
    result = check_arxiv_without_doi(content_by_page, total_pages)
    all_warnings.extend(result.get('warnings', []))

    # 2.9 摘要
    result = check_abstracts(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.10 文本对齐
    result = check_text_alignment(content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    alignment_issues = result.get('result', {}).get('alignment_issues', [])

    # 2.11 图表页面（仅信息收集，不产生警告）
    check_figure_pages(content_by_page)

    # 2.12 字体与行间距
    result = check_font_and_spacing(content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    spacing_info = result.get('result', {})

    # 2.13 字体检测 (使用 PyMuPDF)
    result = check_fonts(pdf_path, content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    font_info = result.get('result', {})

    # 2.14 详细间距分析 (图表、公式与正文间距)
    result = analyze_detailed_spacing(pdf_path, content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    detailed_spacing_info = result

    # 合并所有警告到问题列表
    all_issues.extend(all_warnings)

    # 下方空白页面单独作为统计信息添加到 issues（详细信息在独立区域展示）
    if bottom_blank_pages:
        all_issues.append(
            f"发现 {len(bottom_blank_pages)} 页可能存在下方空白 / Found {len(bottom_blank_pages)} pages possibly with blank space at bottom"
        )

    all_warnings = []

    # 3. 生成控制台报告
    print("\n" + "=" * 60)
    print("论文格式检测报告 / Thesis Format Audit Report")
    print("=" * 60)
    print(f"\nPDF 路径: {pdf_path}")
    print(f"总页数: {total_pages}")
    print(f"平均每页字符数: {average_chars:.1f}")

    if all_issues:
        print("\n\n" + "=" * 60)
        print("❌ 问题项 / Issues Found:")
        print("=" * 60)
        for issue in all_issues:
            print(f"  • {issue}")

    if not all_issues:
        print("\n\n✅ 未发现格式问题")

    print("\n" + "=" * 60)
    print("检测完成")
    print("=" * 60)

    # 4. 生成 HTML 报告
    print("\n" + "=" * 60)
    print("生成报告 / Generating Report")
    print("=" * 60)

    html_path = generate_html_report(
        pdf_path, total_pages, average_chars,
        all_issues,
        bottom_blank_pages, alignment_issues, missing_transitions, spacing_info, font_info, detailed_spacing_info, output_dir
    )

    return {
        'html_path': html_path,
        'issues': all_issues
    }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]")
        print("\n参数说明:")
        print("  pdf_path     - 必填，论文PDF文件路径")
        print("  output_dir   - 可选，报告输出目录（默认当前目录）")
        print("  --type       - 可选，论文类型: cn=中文论文（默认）, en=英文论文")
        print("\n示例:")
        print("  python3 thesis_audit_script.py thesis.pdf")
        print("  python3 thesis_audit_script.py thesis.pdf /output/dir")
        print("  python3 thesis_audit_script.py thesis.pdf --type en")
        print("  python3 thesis_audit_script.py thesis.pdf -t cn")
        sys.exit(1)

    # 解析参数
    pdf_path = None
    output_dir = "."
    thesis_type = "cn"

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--type" or sys.argv[i] == "-t":
            if i + 1 < len(sys.argv):
                thesis_type = sys.argv[i + 1].lower()
                if thesis_type not in ["cn", "en"]:
                    print(f"错误: thesis_type 必须是 'cn' 或 'en'，得到 '{thesis_type}'")
                    sys.exit(1)
                i += 2
            else:
                print("错误: --type 需要一个值 (cn 或 en)")
                sys.exit(1)
        elif sys.argv[i].startswith("-"):
            print(f"错误: 未知参数 '{sys.argv[i]}'")
            sys.exit(1)
        elif pdf_path is None:
            pdf_path = sys.argv[i]
            i += 1
        else:
            output_dir = sys.argv[i]
            i += 1

    if pdf_path is None:
        print("错误: 请提供PDF文件路径")
        sys.exit(1)

    thesis_type_name = "中文论文" if thesis_type == "cn" else "English Thesis"
    print(f"\n论文类型 / Thesis Type: {thesis_type_name}")

    try:
        result = run_full_audit(pdf_path, thesis_type, output_dir)
        print(f"\n📄 报告已生成:")
        print(f"   HTML: {result['html_path']}")
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{pdf_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
