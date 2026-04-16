"""低内容页面检测"""
import re
from typing import List, Dict


def check_low_content_pages(content_by_page: List[Dict], average_chars: float) -> Dict:
    """
    检查低内容页面 (<20% 平均字符数) 和下方空白

    Returns:
        Dict with keys: low_pages, bottom_blank_pages, warnings
    """
    threshold = average_chars * 0.2
    low_pages = []
    bottom_blank_pages = []

    for content in content_by_page:
        # 跳过标准格式页面："攻读硕士学位期间取得的研究成果 - 无"
        if '攻读硕士学位期间取得的研究成果' in content['text']:
            continue

        if 0 < content['chars'] < threshold:
            low_pages.append({
                'page': content['page'],
                'chars': content['chars'],
                'avg': average_chars,
                'sample': content['text'][:150] if content['text'] else ''
            })

    # 检查页面下方空白（内容在顶部，底部大片空白）
    for content in content_by_page:
        lines = content['text'].split('\n') if content['text'] else []

        has_figure = 'Figure' in content['text']
        has_table = bool(re.search(r'Table\s+\d+', content['text']) or
                       re.search(r'表格', content['text']) or
                       re.search(r'表\s*\d+', content['text']))

        if 0 < content['chars'] < threshold and not (has_figure or has_table):
            continue

        if len(lines) < 5:
            continue

        last_lines = [l for l in lines[-5:] if len(l.strip()) > 0]
        if len(last_lines) >= 3:
            short_last_lines = [l for l in last_lines if len(l.strip()) < 15]
            if len(short_last_lines) >= 3:
                # Find content just before the blank area (first short line)
                content_before_blank = short_last_lines[0][:80] if short_last_lines else ''
                bottom_blank_pages.append({
                    'page': content['page'],
                    'chars': content['chars'],
                    'short_lines': len(short_last_lines),
                    'total_lines': len(last_lines),
                    'position': '页面结尾 / End of Page',
                    'content_before_blank': content_before_blank,
                    'reason': 'short_lines'
                })

        # 检查是否包含Figure或Table
        has_figure = 'Figure' in content['text']
        has_table = bool(re.search(r'Table\s+\d+', content['text']) or
                       re.search(r'表格', content['text']) or
                       re.search(r'表\s*\d+', content['text']))

        # List of Figures/Tables 页面检测
        is_list_page = False
        if content['page'] <= 30:
            figure_count = len(re.findall(r'Figure\s+\d+', content['text']))
            table_count = len(re.findall(r'Table\s+\d+', content['text']))
            if figure_count >= 3 or table_count >= 3:
                is_list_page = True

        if is_list_page:
            continue

        if has_figure or has_table:
            last_figure_line = None
            last_figure_idx = -1
            for idx, line in enumerate(lines):
                line_stripped = line.strip()
                if line_stripped and len(line_stripped) > 5:
                    if 'Figure' in line_stripped or 'Table' in line_stripped or '表' in line_stripped:
                        last_figure_line = line_stripped
                        last_figure_idx = idx

            if last_figure_line and last_figure_idx >= 0:
                lines_after_figure = 0
                for i in range(last_figure_idx + 1, len(lines)):
                    line = lines[i].strip()
                    if len(line) > 50:
                        lines_after_figure += 1

                if lines_after_figure >= 2:
                    non_empty_lines = len([l for l in lines if l.strip()])
                    if non_empty_lines <= 15 and content['chars'] < 1200:
                        if not any(bp['page'] == content['page'] for bp in bottom_blank_pages):
                            # Determine position: figure or table
                            if 'Figure' in last_figure_line or '图' in last_figure_line:
                                position = '图片后方 / After Figure'
                            elif 'Table' in last_figure_line or '表' in last_figure_line:
                                position = '表格后方 / After Table'
                            else:
                                position = '图片/表格后方 / After Figure/Table'
                            bottom_blank_pages.append({
                                'page': content['page'],
                                'chars': content['chars'],
                                'short_lines': 0,
                                'total_lines': non_empty_lines,
                                'position': position,
                                'content_before_blank': last_figure_line[:100] if last_figure_line else '',
                                'reason': 'figure_bottom'
                            })
                    continue

                if content['chars'] < 1500:
                    if not any(bp['page'] == content['page'] for bp in bottom_blank_pages):
                        # Determine position: figure or table
                        if 'Figure' in last_figure_line or '图' in last_figure_line:
                            position = '图片后方 / After Figure'
                        elif 'Table' in last_figure_line or '表' in last_figure_line:
                            position = '表格后方 / After Table'
                        else:
                            position = '图片/表格后方 / After Figure/Table'
                        bottom_blank_pages.append({
                            'page': content['page'],
                            'chars': content['chars'],
                            'short_lines': 0,
                            'total_lines': len([l for l in lines if l.strip()]),
                            'position': position,
                            'content_before_blank': last_figure_line[:100] if last_figure_line else '',
                            'reason': 'figure_bottom'
                        })

    warnings = []

    if low_pages:
        warnings.append(f"发现 {len(low_pages)} 页内容低于平均的20% / Found {len(low_pages)} pages with content below 20% of average")
        print(f"⚠️  发现 {len(low_pages)} 页内容异常低")
        for lp in low_pages[:10]:
            print(f"   - 第 {lp['page']} 页: {lp['chars']} 字符 (平均: {lp['avg']:.0f})")
            print(f"     内容: {lp['sample'][:80]}...")
    else:
        print("✅ 所有页面内容正常")

    # Note: bottom_blank_pages are NOT added to warnings here
    # They are shown in the dedicated "Page with Many Empty Rows" section
    if bottom_blank_pages:
        print(f"⚠️  发现 {len(bottom_blank_pages)} 页可能存在下方空白:")
        for bp in bottom_blank_pages[:5]:
            print(f"   - 第{bp['page']}页: {bp['chars']} 字符, 末尾短行: {bp['short_lines']}/{bp['total_lines']}")
            print(f"     最后行: {bp.get('content_before_blank', 'N/A')}...")

    return {
        'low_pages': low_pages,
        'bottom_blank_pages': bottom_blank_pages,
        'warnings': warnings
    }
