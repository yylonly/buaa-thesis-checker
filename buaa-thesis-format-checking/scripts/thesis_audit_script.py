#!/usr/bin/env python3
"""
北京航空航天大学硕士学位论文格式检测脚本
BUAA Master's Thesis Format Audit Script

使用方法:
    # 完整流程
    python3 thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]

    # 分步执行
    python3 thesis_audit_script.py --step1 <pdf_path> [output_dir]    # Step 1: 提取PDF文本
    python3 thesis_audit_script.py --step2 <text_path> --type cn|en   # Step 2: 执行格式检测
    python3 thesis_audit_script.py --step3 <results_path> <pdf_path>   # Step 3: 生成报告
"""

import sys
import os
import json
from datetime import datetime

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


# 临时文件路径
TEMP_TEXT_FILE = "thesis_text_extracted.json"
TEMP_RESULTS_FILE = "thesis_check_results.json"


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
        'issues': all_issues,
        'total_pages': total_pages,
        'average_chars': average_chars,
        'bottom_blank_pages': bottom_blank_pages,
        'alignment_issues': alignment_issues,
        'missing_transitions': missing_transitions,
        'spacing_info': spacing_info,
        'font_info': font_info,
        'detailed_spacing_info': detailed_spacing_info
    }


def run_step1(pdf_path: str, output_dir: str = ".") -> dict:
    """Step 1: 提取PDF文本并保存到临时文件"""
    print("\n" + "=" * 60)
    print("Step 1: 提取PDF文本 / Extracting PDF Text")
    print("=" * 60)

    extractor = ContentExtractor(pdf_path)
    content_by_page = extractor.extract_all()
    total_pages = extractor.total_pages
    average_chars = extractor.average_chars

    # 构建文本数据
    text_data = {
        'pdf_path': pdf_path,
        'total_pages': total_pages,
        'average_chars': average_chars,
        'content_by_page': content_by_page,
        'extracted_at': datetime.now().isoformat()
    }

    # 保存到临时文件
    text_file_path = os.path.join(output_dir, TEMP_TEXT_FILE)
    with open(text_file_path, 'w', encoding='utf-8') as f:
        json.dump(text_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ PDF文本已提取并保存到: {text_file_path}")
    print(f"   总页数: {total_pages}")
    print(f"   平均每页字符数: {average_chars:.1f}")

    return {'text_file': text_file_path, 'total_pages': total_pages}


def run_step2(text_path: str, thesis_type: str = "cn") -> dict:
    """Step 2: 从临时文件加载文本并执行各项检测"""
    print("\n" + "=" * 60)
    print("Step 2: 执行格式检测 / Running Format Checks")
    print("=" * 60)

    # 从临时文件加载文本数据
    with open(text_path, 'r', encoding='utf-8') as f:
        text_data = json.load(f)

    pdf_path = text_data['pdf_path']
    content_by_page = text_data['content_by_page']
    total_pages = text_data['total_pages']
    average_chars = text_data['average_chars']

    print(f"   已加载PDF: {pdf_path}")
    print(f"   总页数: {total_pages}")

    # 收集结果
    all_issues = []
    all_warnings = []
    section_info = {}
    bottom_blank_pages = []
    alignment_issues = []

    print("\n执行各项检测...")

    # 2.1 空白页面
    print("  [1/14] 空白页面检测...")
    result = check_blank_pages(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.2 占位符
    print("  [2/14] 占位符检测...")
    result = check_placeholders(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.3 章节连续性
    print("  [3/14] 章节连续性检测...")
    result = check_section_continuity(content_by_page)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))
    section_info = {
        'sections': result.get('sections', []),
        'chapter_pages': result.get('chapter_pages', {}),
        'missing_chapters': result.get('missing_chapters', [])
    }

    # 2.4 低内容页面
    print("  [4/14] 低内容页面检测...")
    result = check_low_content_pages(content_by_page, average_chars)
    all_warnings.extend(result.get('warnings', []))
    bottom_blank_pages = result.get('bottom_blank_pages', [])

    # 2.5 未完成标记
    print("  [5/14] 未完成标记检测...")
    result = check_incomplete_content(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.6 过渡段
    print("  [6/14] 过渡段检测...")
    result = check_transition_paragraphs(content_by_page)
    all_warnings.extend(result.get('warnings', []))
    missing_transitions = result.get('result', {}).get('missing_transitions', [])

    # 2.7 URL 位置
    print("  [7/14] URL位置检测...")
    result = check_urls_in_body(content_by_page, total_pages)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))

    # 2.8 arXiv DOI
    print("  [8/14] arXiv DOI检测...")
    result = check_arxiv_without_doi(content_by_page, total_pages)
    all_warnings.extend(result.get('warnings', []))

    # 2.9 摘要
    print("  [9/14] 摘要检测...")
    result = check_abstracts(content_by_page)
    all_warnings.extend(result.get('warnings', []))

    # 2.10 文本对齐
    print("  [10/14] 文本对齐检测...")
    result = check_text_alignment(content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    alignment_issues = result.get('result', {}).get('alignment_issues', [])

    # 2.11 图表页面
    print("  [11/14] 图表页面统计...")
    check_figure_pages(content_by_page)

    # 2.12 字体与行间距
    print("  [12/14] 字体与行间距检测...")
    result = check_font_and_spacing(content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    spacing_info = result.get('result', {})

    # 2.13 字体检测
    print("  [13/14] 字体检测...")
    result = check_fonts(pdf_path, content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    font_info = result.get('result', {})

    # 2.14 详细间距分析
    print("  [14/14] 详细间距分析...")
    result = analyze_detailed_spacing(pdf_path, content_by_page, thesis_type)
    all_warnings.extend(result.get('warnings', []))
    detailed_spacing_info = result

    # 合并所有警告到问题列表
    all_issues.extend(all_warnings)

    # 下方空白页面
    if bottom_blank_pages:
        all_issues.append(
            f"发现 {len(bottom_blank_pages)} 页可能存在下方空白 / Found {len(bottom_blank_pages)} pages possibly with blank space at bottom"
        )

    # 构建检测结果
    check_results = {
        'pdf_path': pdf_path,
        'thesis_type': thesis_type,
        'total_pages': total_pages,
        'average_chars': average_chars,
        'all_issues': all_issues,
        'all_warnings': all_warnings,
        'section_info': section_info,
        'bottom_blank_pages': bottom_blank_pages,
        'alignment_issues': alignment_issues,
        'missing_transitions': missing_transitions,
        'spacing_info': spacing_info,
        'font_info': font_info,
        'detailed_spacing_info': detailed_spacing_info,
        'checked_at': datetime.now().isoformat()
    }

    # 保存到临时文件
    results_file_path = TEMP_RESULTS_FILE
    with open(results_file_path, 'w', encoding='utf-8') as f:
        json.dump(check_results, f, ensure_ascii=False, indent=2)

    # 打印检测摘要
    print("\n" + "=" * 60)
    print("检测摘要 / Check Summary")
    print("=" * 60)
    print(f"  总页数: {total_pages}")
    print(f"  问题数: {len([i for i in all_issues if not i.startswith('发现')])}")
    print(f"  警告数: {len(all_warnings)}")

    print(f"\n✅ 检测结果已保存到: {results_file_path}")

    return {'results_file': results_file_path, 'issue_count': len(all_issues), 'warning_count': len(all_warnings)}


def run_step3(results_path: str, pdf_path: str = None, output_dir: str = ".") -> dict:
    """Step 3: 从检测结果生成报告"""
    print("\n" + "=" * 60)
    print("Step 3: 生成报告 / Generating Report")
    print("=" * 60)

    # 从临时文件加载检测结果
    with open(results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)

    if pdf_path is None:
        pdf_path = results.get('pdf_path', 'unknown')

    total_pages = results.get('total_pages', 0)
    average_chars = results.get('average_chars', 0)
    all_issues = results.get('all_issues', [])
    bottom_blank_pages = results.get('bottom_blank_pages', [])
    alignment_issues = results.get('alignment_issues', [])
    missing_transitions = results.get('missing_transitions', [])
    spacing_info = results.get('spacing_info', {})
    font_info = results.get('font_info', {})
    detailed_spacing_info = results.get('detailed_spacing_info', {})

    # 生成控制台报告
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

    # 生成HTML报告
    html_path = generate_html_report(
        pdf_path, total_pages, average_chars,
        all_issues,
        bottom_blank_pages, alignment_issues, missing_transitions,
        spacing_info, font_info, detailed_spacing_info, output_dir
    )

    print(f"\n✅ 报告已生成: {html_path}")

    return {'html_path': html_path}


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  # 完整流程")
        print("  python3 thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]")
        print("")
        print("  # 分步执行")
        print("  python3 thesis_audit_script.py --step1 <pdf_path> [output_dir]")
        print("  python3 thesis_audit_script.py --step2 <text_path> --type cn|en")
        print("  python3 thesis_audit_script.py --step3 <results_path> [pdf_path]")
        print("")
        print("参数说明:")
        print("  --step1       - Step 1: 提取PDF文本到临时文件")
        print("  --step2       - Step 2: 从临时文件加载并执行格式检测")
        print("  --step3       - Step 3: 从检测结果生成报告")
        print("  pdf_path      - 论文PDF文件路径")
        print("  text_path     - Step1生成的临时文本文件")
        print("  results_path  - Step2生成的检测结果文件")
        print("  output_dir    - 报告输出目录（默认当前目录）")
        print("  --type / -t  - 论文类型: cn=中文论文（默认）, en=英文论文")
        print("")
        print("示例:")
        print("  # 完整流程")
        print("  python3 thesis_audit_script.py thesis.pdf")
        print("  python3 thesis_audit_script.py thesis.pdf /output/dir --type cn")
        print("")
        print("  # 分步执行")
        print("  python3 thesis_audit_script.py --step1 thesis.pdf")
        print("  python3 thesis_audit_script.py --step2 thesis_text_extracted.json --type cn")
        print("  python3 thesis_audit_script.py --step3 thesis_check_results.json thesis.pdf")
        sys.exit(1)

    # 检查是否为分步执行模式
    if sys.argv[1] == "--step1":
        # Step 1: 提取PDF文本
        if len(sys.argv) < 3:
            print("错误: --step1 需要指定PDF文件路径")
            sys.exit(1)
        pdf_path = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "."

        try:
            result = run_step1(pdf_path, output_dir)
            print(f"\n✅ Step 1 完成!")
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{pdf_path}'")
            sys.exit(1)
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif sys.argv[1] == "--step2":
        # Step 2: 执行格式检测
        if len(sys.argv) < 3:
            print("错误: --step2 需要指定文本文件路径")
            sys.exit(1)
        text_path = sys.argv[2]

        # 解析剩余参数
        thesis_type = "cn"
        i = 3
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
            else:
                i += 1

        thesis_type_name = "中文论文" if thesis_type == "cn" else "English Thesis"
        print(f"\n论文类型 / Thesis Type: {thesis_type_name}")

        try:
            result = run_step2(text_path, thesis_type)
            print(f"\n✅ Step 2 完成!")
            print(f"   问题数: {result['issue_count']}")
            print(f"   警告数: {result['warning_count']}")
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{text_path}'")
            sys.exit(1)
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif sys.argv[1] == "--step3":
        # Step 3: 生成报告
        if len(sys.argv) < 3:
            print("错误: --step3 需要指定结果文件路径")
            sys.exit(1)
        results_path = sys.argv[2]
        pdf_path = sys.argv[3] if len(sys.argv) > 3 else None
        output_dir = sys.argv[4] if len(sys.argv) > 4 else "."

        try:
            result = run_step3(results_path, pdf_path, output_dir)
            print(f"\n✅ Step 3 完成!")
            print(f"   报告: {result['html_path']}")
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{results_path}'")
            sys.exit(1)
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    else:
        # 完整流程模式
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
