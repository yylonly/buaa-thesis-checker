"""未完成内容标记检测"""
import re
from typing import List, Dict


def check_incomplete_content(content_by_page: List[Dict]) -> Dict:
    """
    检查未完成内容标记 (to be continued, WIP, etc.)

    Returns:
        Dict with keys: found_incomplete, warnings
    """
    # 这些模式表示"未完成"含义，用于标记论文未写完
    # 使用精确匹配，避免误报
    incomplete_indicators = [
        (r'to be continued', 'to be continued'),
        (r'T\.B\.C\.', 'T.B.C.'),  # 常见变体
        (r'TBC\b', 'TBC'),
        (r'WIP\b', 'WIP'),
        (r'under\s+construction', 'under construction'),
        (r'work\s+in\s+progress', 'work in progress'),
        (r'未完$', '未完'),  # 中文"未完"单独出现
        (r'待续', '待续'),  # 中文"待续"
    ]

    # 排除的页面类型（不检查这些页面）
    # 摘要页、目录页、图表清单等可能出现英文术语但不是未完成标记
    exclude_pages = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}

    found_incomplete = []

    for content in content_by_page:
        page_num = content['page']
        # 跳过目录、摘要、图表清单、缩略语等页面
        if page_num in exclude_pages:
            continue

        if content['text']:
            text = content['text']
            text_lower = text.lower()

            for pattern, name in incomplete_indicators:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    found_incomplete.append({
                        'page': page_num,
                        'pattern': name,
                        'context': text[:200]
                    })

    warnings = []

    if found_incomplete:
        warnings.append(f"发现 {len(found_incomplete)} 处未完成标记 / Found {len(found_incomplete)} incomplete markers")
        print(f"⚠️  发现未完成内容标记:")
        for fi in found_incomplete:
            print(f"   - 第 {fi['page']} 页: '{fi['pattern']}'")
            print(f"     上下文: {fi['context'][:100]}...")
    else:
        print("✅ 未发现未完成内容标记")

    return {
        'found_incomplete': found_incomplete,
        'warnings': warnings
    }
