"""正文 URL 检测"""
import re
from typing import List, Dict


def check_urls_in_body(content_by_page: List[Dict], total_pages: int) -> Dict:
    """
    检查正文中的 URL（URL 应在脚注中，而非正文）

    Returns:
        Dict with keys: urls_in_body, issues, warnings
    """
    url_pattern = re.compile(r'https?://[^\s\)"\']+')
    ref_start_page = max(1, total_pages - 40)

    urls_in_body = []

    for content in content_by_page:
        if not content['text']:
            continue
        if content['page'] >= ref_start_page:
            continue

        urls = url_pattern.findall(content['text'])
        if urls:
            for url in urls:
                urls_in_body.append({
                    'page': content['page'],
                    'url': url[:80] + '...' if len(url) > 80 else url,
                    'full_url': url
                })

    issues = []
    warnings = []

    if urls_in_body:
        issues.append(f"发现 {len(urls_in_body)} 处URL在正文中（应在脚注） / Found {len(urls_in_body)} URLs in body text (should be in footnotes)")
        warnings.append(f"发现 {len(urls_in_body)} 处URL在正文中（应在脚注） / Found {len(urls_in_body)} URLs in body text (should be in footnotes)")
        print(f"⚠️  发现 {len(urls_in_body)} 处URL在正文中，应在脚注中:")
        for item in urls_in_body[:10]:
            print(f"   - 第 {item['page']} 页: {item['url']}")
    else:
        print("✅ 正文中的URL已正确移至脚注")

    return {
        'urls_in_body': urls_in_body,
        'total': len(urls_in_body),
        'issues': issues,
        'warnings': warnings
    }
