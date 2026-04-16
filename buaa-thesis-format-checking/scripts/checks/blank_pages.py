"""空白页面检测"""
from typing import List, Dict


def check_blank_pages(content_by_page: List[Dict]) -> Dict:
    """
    检查空白页面和低内容页面

    Returns:
        Dict with keys: blank_pages, low_content_pages, issues, warnings
    """
    blank_pages = []
    low_content_pages = []

    for content in content_by_page:
        if content['chars'] == 0:
            blank_pages.append(content['page'])
        elif content['chars'] < 50:
            low_content_pages.append({
                'page': content['page'],
                'chars': content['chars'],
                'sample': content['text'][:100] if content['text'] else ''
            })

    issues = []
    warnings = []

    if blank_pages:
        warnings.append(f"发现 {len(blank_pages)} 个空白页: {blank_pages} / Found {len(blank_pages)} blank pages")
        print(f"⚠️  发现 {len(blank_pages)} 个空白页")
        for bp in blank_pages:
            print(f"   - 第 {bp} 页")
    else:
        print("✅ 未发现空白页")

    if low_content_pages:
        warnings.append(f"发现 {len(low_content_pages)} 个低内容页 (<50字符) / Found {len(low_content_pages)} low-content pages (<50 chars)")
        print(f"⚠️  发现 {len(low_content_pages)} 个低内容页")
        for lcp in low_content_pages[:5]:
            print(f"   - 第 {lcp['page']} 页: {lcp['chars']} 字符")

    return {
        'blank_pages': blank_pages,
        'low_content_pages': low_content_pages,
        'issues': issues,
        'warnings': warnings
    }
