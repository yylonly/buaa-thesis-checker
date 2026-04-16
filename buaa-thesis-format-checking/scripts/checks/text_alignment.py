"""文本对齐方式检测"""
import re
import statistics
from typing import List, Dict


def check_text_alignment(content_by_page: List[Dict], thesis_type: str = "cn") -> Dict:
    """
    检测正文文本对齐方式（两端对齐 vs 左对齐）

    Returns:
        Dict with keys: result, warnings
    """
    result = {
        'likely_justified': False,
        'likely_left_aligned': False,
        'analyzed_pages': 0,
        'line_ending_variance': 0,
        'avg_line_length': 0,
        'chinese_abstract_alignment': None
    }

    body_pages = content_by_page[5:min(50, len(content_by_page) - 50)]
    abstract_pages = content_by_page[:5]

    all_line_lengths = []
    chinese_abstract_align = None
    # Track per-page alignment status with page numbers
    page_alignment_details = []

    for content in body_pages:
        if not content['text'] or content['chars'] < 200:
            continue

        lines = content['text'].split('\n')
        page_line_lengths = []

        for line in lines:
            line = line.rstrip()
            if len(line) > 20:
                line_length = len(line)
                page_line_lengths.append(line_length)
                all_line_lengths.append(line_length)

        if page_line_lengths and len(page_line_lengths) > 3:
            avg_len = sum(page_line_lengths) / len(page_line_lengths)
            stdev = statistics.stdev(page_line_lengths) if len(page_line_lengths) > 1 else 0
            cv = stdev / avg_len if avg_len > 0 else 1
            is_justified = cv < 0.15
            page_alignment_details.append({
                'page': content['page'],
                'cv': round(cv, 4),
                'is_justified': is_justified,
                'avg_length': round(avg_len, 1)
            })
            result['analyzed_pages'] += 1

    for content in abstract_pages:
        if not content['text'] or content['chars'] < 100:
            continue

        if '独创性声明' in content['text'] or '授权说明' in content['text']:
            continue

        lines = content['text'].split('\n')[:5]
        has_abstract_keyword = any('摘要' in line or '摘 要' in line for line in lines)

        if not has_abstract_keyword:
            continue

        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', content['text']))
        if chinese_chars < 50:
            continue

        lines = content['text'].split('\n')
        abstract_page_lengths = []

        for line in lines:
            line = line.rstrip()
            if len(line) > 15:
                abstract_page_lengths.append(len(line))

        if abstract_page_lengths and len(abstract_page_lengths) >= 3:
            avg_len = statistics.mean(abstract_page_lengths)
            std_len = statistics.stdev(abstract_page_lengths)
            cv = std_len / avg_len if avg_len > 0 else 1

            chinese_abstract_align = {
                'page': content['page'],
                'cv': round(cv, 4),
                'avg_length': round(avg_len, 1),
                'is_justified': cv < 0.15
            }
            break

    warnings = []
    left_aligned_pages = []

    if all_line_lengths:
        avg_length = statistics.mean(all_line_lengths)
        stdev = statistics.stdev(all_line_lengths)
        variance = statistics.variance(all_line_lengths)

        result['avg_line_length'] = round(avg_length, 1)
        result['line_ending_variance'] = round(variance, 1)

        if avg_length > 0:
            coefficient_of_variation = stdev / avg_length

            if coefficient_of_variation < 0.25:
                result['likely_justified'] = True
                result['likely_left_aligned'] = False
                align_type = "两端对齐 (Justified)"
            else:
                result['likely_justified'] = False
                result['likely_left_aligned'] = True
                align_type = "左对齐 (Left-aligned)"

            print(f"\n   文本对齐分析:")
            print(f"      平均行长度: {result['avg_line_length']} 字符")
            print(f"      长度方差: {result['line_ending_variance']}")
            print(f"      变异系数: {coefficient_of_variation:.2%}")
            print(f"      检测结果: {align_type}")

            # Collect pages with alignment issues
            left_aligned_pages = [p for p in page_alignment_details if not p['is_justified']]

            if thesis_type == "cn":
                if result['likely_left_aligned'] and left_aligned_pages:
                    warnings.append(f"发现 {len(left_aligned_pages)} 页正文可能使用左对齐格式，规范要求中文论文正文应使用两端对齐 / Found {len(left_aligned_pages)} pages possibly left-aligned; Chinese thesis should use justified alignment")
                    print(f"      ⚠️  建议: 中文论文正文应使用两端对齐格式")
                    print(f"      左对齐页面: {', '.join(str(p['page']) for p in left_aligned_pages[:15])}")
                else:
                    print(f"      ✅ 对齐格式符合中文论文规范要求")
            else:
                if result['likely_justified']:
                    print(f"      ✅ 对齐格式符合英文论文规范要求 (推荐使用两端对齐)")
                else:
                    warnings.append(f"发现 {len(left_aligned_pages)} 页正文可能未使用两端对齐格式，英文论文推荐使用两端对齐 / Found {len(left_aligned_pages)} pages possibly not justified; English thesis recommended to use justified alignment")
                    print(f"      ⚠️  建议: 英文论文推荐使用两端对齐 (Justified alignment)")
                    print(f"      左对齐页面: {', '.join(str(p['page']) for p in left_aligned_pages[:15])}")

            if chinese_abstract_align:
                print(f"\n   中文摘要对齐分析 (第{chinese_abstract_align['page']}页):")
                print(f"      变异系数: {chinese_abstract_align['cv']:.2%}")
                if chinese_abstract_align['is_justified']:
                    print(f"      检测结果: 两端对齐 ✅")
                else:
                    print(f"      检测结果: 左对齐 ⚠️")
                    warnings.append(f"中文摘要因使用左对齐格式不规范，规范要求中文摘要应使用两端对齐 / Chinese abstract left-aligned; should use justified alignment")

            print(f"\n   分析页面数: {result['analyzed_pages']} 页")

    elif chinese_abstract_align:
        print(f"\n   中文摘要对齐分析 (第{chinese_abstract_align['page']}页):")
        print(f"      变异系数: {chinese_abstract_align['cv']:.2%}")
        if chinese_abstract_align['is_justified']:
            print(f"      检测结果: 两端对齐 ✅")
        else:
            print(f"      检测结果: 左对齐 ⚠️")
            warnings.append(f"中文摘要因使用左对齐格式不规范，规范要求中文摘要应使用两端对齐 / Chinese abstract left-aligned; should use justified alignment")
    else:
        print(f"   ⚠️  无法分析文本对齐（页面内容不足）")
        result['analyzed_pages'] = 0

    # Build alignment issues list for dedicated table
    alignment_issues = []
    if left_aligned_pages:
        for p in left_aligned_pages:
            alignment_issues.append({
                'page': p['page'],
                'type': '正文 / Body Text',
                'detail': '左对齐 / Left-aligned'
            })
    if chinese_abstract_align and not chinese_abstract_align['is_justified']:
        alignment_issues.append({
            'page': chinese_abstract_align['page'],
            'type': '中文摘要 / Chinese Abstract',
            'detail': '左对齐 / Left-aligned'
        })

    result['chinese_abstract_alignment'] = chinese_abstract_align
    result['page_alignment_details'] = page_alignment_details
    result['alignment_issues'] = alignment_issues

    return {
        'result': result,
        'warnings': warnings
    }
