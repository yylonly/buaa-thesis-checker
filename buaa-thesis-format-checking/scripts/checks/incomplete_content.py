"""未完成内容标记检测"""
from typing import List, Dict


def check_incomplete_content(content_by_page: List[Dict]) -> Dict:
    """
    检查未完成内容标记 (to be continued, WIP, etc.)

    Returns:
        Dict with keys: found_incomplete, warnings
    """
    incomplete_patterns = [
        'to be continued', 'continued', 'TBC',
        'in progress', 'under construction',
        'WIP', 'work in progress'
    ]

    found_incomplete = []

    for content in content_by_page:
        if content['text']:
            text_lower = content['text'].lower()
            for pattern in incomplete_patterns:
                if pattern in text_lower:
                    found_incomplete.append({
                        'page': content['page'],
                        'pattern': pattern,
                        'context': content['text'][:300]
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
