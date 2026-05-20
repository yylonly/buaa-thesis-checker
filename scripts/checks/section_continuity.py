"""章节连续性检测"""
import re
from typing import List, Dict


def check_section_continuity(content_by_page: List[Dict]) -> Dict:
    """
    检查章节连续性 (Chapter 1-5 或 第一章-第五章)

    Returns:
        Dict with keys: sections, chapter_pages, missing_chapters, issues, warnings
    """
    sections = []
    chapter_pages = {}

    # 中文章节标题关键词（与第一章、第二章等配合使用）
    cn_chapter_keywords = ['引言', '结论', '总结', '评估', '评价', '实验', '方法', '相关工作', '背景', '文献']

    for content in content_by_page:
        text = content['text']
        if not text:
            continue

        lines = text.split('\n')

        for line in lines[:10]:
            line = line.strip()
            if not line:
                continue

            # 检测英文 Chapter 模式
            if line.startswith('Chapter ') and any(marker in line for marker in
                ['Introduction', 'Conclusion', 'Evaluation', 'Methodology',
                 'Literature', 'Related', 'Background']):
                sections.append({
                    'page': content['page'],
                    'type': 'chapter',
                    'title': line
                })
                if 'Chapter 1' in line:
                    chapter_pages[1] = content['page']
                elif 'Chapter 2' in line:
                    chapter_pages[2] = content['page']
                elif 'Chapter 3' in line:
                    chapter_pages[3] = content['page']
                elif 'Chapter 4' in line:
                    chapter_pages[4] = content['page']
                elif 'Chapter 5' in line:
                    chapter_pages[5] = content['page']
                break

            # 检测中文 第X章 模式（包括"第一章"、"第一章 绪论"等格式）
            # 匹配 "第" + 中文的 一/二/三/四/五 + "章"，后面可能有空格和标题
            cn_chapter_match = re.match(r'^第([一二三四五])章', line)
            if cn_chapter_match:
                chapter_num_str = cn_chapter_match.group(1)

                # 转换中文数字到阿拉伯数字
                cn_to_num = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5}
                chapter_num = cn_to_num.get(chapter_num_str)

                # 跳过目录页（页码3-15范围内，包含引导线"····"的是目录页）
                page_num = content['page']
                # 目录页特征：包含多个 · 字符（中日韩点）构成的引导线
                is_toc_page = page_num <= 15 and text.count('·') >= 5

                # 只记录第一次出现的章节页（忽略目录页的重复）
                if chapter_num and chapter_num not in chapter_pages and not is_toc_page:
                    chapter_pages[chapter_num] = content['page']
                    sections.append({
                        'page': content['page'],
                        'type': 'chapter',
                        'title': line.strip()
                    })
                    # 找到就break，避免同一页重复检测
                    break
                elif chapter_num and not is_toc_page:
                    # 已记录过，但仍记录section
                    sections.append({
                        'page': content['page'],
                        'type': 'chapter',
                        'title': line.strip()
                    })

            if line.startswith('Acknowledgements') or line.startswith('Acknowledgement'):
                sections.append({
                    'page': content['page'],
                    'type': 'acknowledgements',
                    'title': line
                })
                break
            elif line.startswith('References'):
                sections.append({
                    'page': content['page'],
                    'type': 'references',
                    'title': line
                })
                break

    print(f"检测到 {len(sections)} 个章节标记")
    print(f"检测到 {len(chapter_pages)} 个编号章节")

    # 不再假设必须有1-5章，只报告发现的内容
    found_chapters = sorted(chapter_pages.keys())
    missing_chapters = []

    warnings = []
    issues = []

    # 如果完全没有检测到章节，报告警告
    if not chapter_pages and not sections:
        warnings.append("未能检测到章节结构，请人工核实 / No chapter structure detected, please verify manually")
        print(f"⚠️  未能检测到章节结构")

    # 如果检测到章节数少于3个，报告警告
    if 0 < len(chapter_pages) < 3:
        warnings.append(f"检测到章节数偏少（{len(chapter_pages)}个），可能存在检测遗漏 / Few chapters detected ({len(chapter_pages)}), possible detection issue")
        print(f"⚠️  检测到章节数偏少，可能存在检测遗漏")

    print("\n章节页面分布:")
    for ch in sorted(chapter_pages.keys()):
        num_str = ['一','二','三','四','五','六','七','八','九','十']
        ch_str = num_str[ch-1] if 1 <= ch <= 10 else str(ch)
        print(f"   第{ch_str}章: 第 {chapter_pages[ch]} 页")

    if sections:
        print("\n其他章节标记:")
        for s in sections[:10]:  # 最多显示10个
            if s['type'] != 'chapter' or s['page'] not in chapter_pages.values():
                print(f"   第{s['page']}页: {s['title'][:50]}")

    return {
        'sections': sections,
        'chapter_pages': chapter_pages,
        'missing_chapters': missing_chapters,
        'issues': issues,
        'warnings': warnings
    }
