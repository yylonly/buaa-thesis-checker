"""图表页面检测"""
from typing import List, Dict


def check_figure_pages(content_by_page: List[Dict]) -> Dict:
    """
    检查图表页面分布

    Returns:
        Dict with keys: figure_pages, total_figure_pages
    """
    figure_pages = []

    for content in content_by_page:
        if content['text']:
            figure_count = content['text'].count('Figure ')
            table_count = content['text'].count('Table ')

            if figure_count >= 2 or (figure_count >= 1 and content['chars'] < 300):
                figure_pages.append({
                    'page': content['page'],
                    'figure_count': figure_count,
                    'table_count': table_count,
                    'chars': content['chars']
                })

    print(f"检测到 {len(figure_pages)} 页包含大量图表")

    return {
        'figure_pages': figure_pages,
        'total_figure_pages': len(figure_pages)
    }
