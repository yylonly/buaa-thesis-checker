"""占位符检测"""
from typing import List, Dict


def check_placeholders(content_by_page: List[Dict]) -> Dict:
    """
    检查占位符 (XXX, TODO, TBD, ****, placeholder, 待填写)

    Returns:
        Dict with keys: found_placeholders, pages_with_placeholders, warnings
    """
    placeholder_patterns = ['XXX', 'TODO', 'TBD', 'XXXX', '****', 'placeholder', '待填写']
    found_placeholders = []

    for content in content_by_page:
        if content['text']:
            for pattern in placeholder_patterns:
                if pattern in content['text']:
                    found_placeholders.append({
                        'page': content['page'],
                        'pattern': pattern,
                        'context': content['text'][:200]
                    })

    warnings = []

    if found_placeholders:
        pages_with_placeholders = {}
        for fp in found_placeholders:
            page = fp['page']
            if page not in pages_with_placeholders:
                pages_with_placeholders[page] = []
            pages_with_placeholders[page].append(fp['pattern'])

        warnings.append(f"发现 {len(pages_with_placeholders)} 页包含占位符 / Found {len(pages_with_placeholders)} pages with placeholders")
        print(f"⚠️  发现 {len(pages_with_placeholders)} 页包含占位符")
        for page, patterns in pages_with_placeholders.items():
            print(f"   - 第 {page} 页: {set(patterns)}")
    else:
        print("✅ 未发现占位符")

    return {
        'found_placeholders': found_placeholders,
        'pages_with_placeholders': found_placeholders,  # alias for compatibility
        'warnings': warnings
    }
