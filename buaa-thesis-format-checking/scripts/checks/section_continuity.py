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

                # 只记录第一次出现的章节页（忽略目录页的重复）
                if chapter_num and chapter_num not in chapter_pages:
                    chapter_pages[chapter_num] = content['page']
                    sections.append({
                        'page': content['page'],
                        'type': 'chapter',
                        'title': line.strip()
                    })
                    # 找到就break，避免同一页重复检测
                    break
                elif chapter_num:
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

    expected_chapters = [1, 2, 3, 4, 5]
    found_chapters = sorted(chapter_pages.keys())
    missing_chapters = set(expected_chapters) - set(found_chapters)

    issues = []
    warnings = []

    if missing_chapters:
        # 根据检测到的章节类型生成合适的错误信息
        has_cn = any(cn_to_num.get(str(ch)) for ch in found_chapters if isinstance(ch, str))
        if found_chapters:
            issues.append(f"缺失章节: 第{', '.join(['一' if c==1 else '二' if c==2 else '三' if c==3 else '四' if c==4 else '五' for c in missing_chapters])}章")
        else:
            issues.append(f"缺失章节: Chapter {missing_chapters}")
        print(f"⚠️  缺失章节: {missing_chapters}")
    else:
        print(f"✅ 所有章节 (1-5) 均已找到")

    print("\n章节页面分布:")
    for ch in sorted(chapter_pages.keys()):
        print(f"   第{['一','二','三','四','五'][ch-1]}章: 第 {chapter_pages[ch]} 页")

    return {
        'sections': sections,
        'chapter_pages': chapter_pages,
        'missing_chapters': list(missing_chapters),
        'issues': issues,
        'warnings': warnings
    }
