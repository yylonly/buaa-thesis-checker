"""过渡段检测"""
import re
from typing import List, Dict


def check_transition_paragraphs(content_by_page: List[Dict]) -> Dict:
    """
    检查二级与三级标题之间是否有过渡段

    二级标题: X.X (如 1.1, 2.3)
    三级标题: X.X.X (如 1.1.1, 2.3.4)

    Returns:
        Dict with keys: result, warnings
    """
    heading_pattern = re.compile(r'^(\d+\.\d+)\s+[\u4e00-\u9fa5a-zA-Z]')
    section_pattern = re.compile(r'^(\d+\.\d+\.\d+)\s+[\u4e00-\u9fa5a-zA-Z]')

    toc_indicator_patterns = [
        'Table of Contents', '目  录', '目 录', 'CONTENTS', 'List of Figure', 'List of Table',
        '图目录', '参考文献', 'Acknowledgement', '致谢'
    ]

    all_headings = []
    toc_pages = set()

    # 识别目录页
    for content in content_by_page[:30]:
        if not content['text']:
            continue
        text_sample = content['text'][:1000]

        is_toc = False
        for pattern in toc_indicator_patterns:
            if pattern in text_sample:
                is_toc = True
                break

        if '........' in text_sample or '⋯⋯' in text_sample or '········' in text_sample:
            is_toc = True

        first_line = text_sample.split('\n')[0].strip() if text_sample else ''
        if first_line in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
                        'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                        'Abstract', '摘要', 'CONTENTS']:
            is_toc = True

        if is_toc:
            toc_pages.add(content['page'])

    print(f"   排除目录/前言页: {sorted(toc_pages)}")

    # 提取正文中的标题
    for content in content_by_page:
        if not content['text']:
            continue
        if content['page'] in toc_pages:
            continue

        lines = content['text'].split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            section_match = section_pattern.match(line)
            if section_match:
                all_headings.append({
                    'page': content['page'],
                    'level': 3,
                    'number': section_match.group(1),
                    'title': line,
                    'is_transition': False
                })
                continue

            heading_match = heading_pattern.match(line)
            if heading_match:
                all_headings.append({
                    'page': content['page'],
                    'level': 2,
                    'number': heading_match.group(1),
                    'title': line,
                    'is_transition': False
                })

    # 检查过渡段
    missing_transitions = []
    last_level2 = None  # Track the most recent level-2 heading in document order

    for heading in all_headings:
        if heading['level'] == 2:
            last_level2 = heading
        elif heading['level'] == 3:
            current_page_idx = heading['page'] - 1
            current_page_content = content_by_page[current_page_idx]['text']
            page_lines = current_page_content.split('\n')

            heading_line_idx = -1
            for idx, line in enumerate(page_lines):
                if heading['title'][:25] in line:
                    heading_line_idx = idx
                    break

            has_transition = False
            if heading_line_idx >= 0:
                preceding_chars = 0
                # If heading is near the start of the page, also check previous page's trailing content
                if heading_line_idx <= 4 and current_page_idx > 0:
                    prev_page_content = content_by_page[current_page_idx - 1]['text']
                    prev_page_lines = prev_page_content.split('\n')
                    # Count non-heading chars from the previous page's last portion
                    for pline in prev_page_lines[-10:]:  # last 10 lines of prev page
                        pline_stripped = pline.strip()
                        if section_pattern.match(pline_stripped) or heading_pattern.match(pline_stripped):
                            break
                        if pline_stripped and not pline_stripped.startswith('Figure'):
                            preceding_chars += len(pline_stripped)

                # Also check current page content before the heading
                for j in range(heading_line_idx - 1, -1, -1):
                    prev_line = page_lines[j].strip()
                    if section_pattern.match(prev_line) or heading_pattern.match(prev_line):
                        break
                    if prev_line and not prev_line.startswith('Figure'):
                        preceding_chars += len(prev_line)

                if preceding_chars >= 60:
                    has_transition = True

            heading['is_transition'] = has_transition

            if not has_transition:
                missing_transitions.append({
                    'page': heading['page'],
                    'level': heading['level'],
                    'number': heading['number'],
                    'title': heading['title'][:60],
                    'parent_level2': last_level2['title'][:60] if last_level2 else ''
                })

    # 去重
    unique_missing = {}
    for mt in missing_transitions:
        key = (mt['page'], mt['number'])
        if key not in unique_missing:
            unique_missing[key] = mt

    missing_transitions = list(unique_missing.values())
    missing_transitions.sort(key=lambda x: (x['page'], x['number']))

    warnings = []

    if missing_transitions:
        warnings.append(f"发现 {len(missing_transitions)} 处缺少过渡段 / Found {len(missing_transitions)} missing transition paragraphs")
        print(f"⚠️  发现 {len(missing_transitions)} 处二级与三级标题之间缺少过渡段:")
        for mt in missing_transitions[:15]:
            print(f"   - 第 {mt['page']} 页: [{mt['number']}] {mt['title']}")
        if len(missing_transitions) > 15:
            print(f"   ... 还有 {len(missing_transitions) - 15} 处省略")
    else:
        print("✅ 所有二级与三级标题之间都有过渡段")

    total_level3 = sum(1 for h in all_headings if h['level'] == 3)
    total_with_transition = sum(1 for h in all_headings if h['is_transition'])

    print(f"\n   三级标题总数: {total_level3}")
    print(f"   有过渡段: {total_with_transition}")
    print(f"   无过渡段: {total_level3 - total_with_transition}")

    return {
        'result': {
            'total_level3_headings': total_level3,
            'with_transition': total_with_transition,
            'without_transition': total_level3 - total_with_transition,
            'missing_transitions': missing_transitions
        },
        'warnings': warnings
    }
