"""arXiv DOI 检测"""
import re
from typing import List, Dict


def check_arxiv_without_doi(content_by_page: List[Dict], total_pages: int) -> Dict:
    """
    检查参考文献中的 arXiv 引用是否已有正式出版物（DOI）

    Returns:
        Dict with keys: arxiv_refs, arxiv_with_doi, arxiv_without_doi, warnings
    """
    ref_start_page = max(1, total_pages - 40)
    arxiv_refs = []

    for content in content_by_page:
        if content['page'] < ref_start_page:
            continue
        if not content['text']:
            continue

        ref_entries = re.findall(r'\[(\d+)\]\s+([^\n]+(?:\n(?!\[\d+\])[^\n]+)*)', content['text'])

        for ref_num, ref_text in ref_entries:
            if 'arXiv' in ref_text or 'arxiv' in ref_text.lower():
                arxiv_match = re.search(r'arXiv[:\s]*([^\s,\]]+)', ref_text, re.IGNORECASE)
                doi_match = re.search(r'DOI[:\s]*([^\s,\]]+)', ref_text, re.IGNORECASE)

                arxiv_id = arxiv_match.group(1) if arxiv_match else "Unknown"
                has_doi = bool(doi_match)
                doi_id = doi_match.group(1) if doi_match else ""

                arxiv_refs.append({
                    'ref_num': f"[{ref_num}]",
                    'page': content['page'],
                    'arxiv_id': arxiv_id,
                    'has_doi': has_doi,
                    'doi': doi_id,
                    'full_text': ref_text[:150]
                })

    arxiv_without_doi = [r for r in arxiv_refs if not r['has_doi']]
    arxiv_with_doi = [r for r in arxiv_refs if r['has_doi']]

    warnings = []

    print(f"   共发现 {len(arxiv_refs)} 条arXiv引用")

    if arxiv_with_doi:
        print(f"   ✅ 有DOI（已正式发表）: {len(arxiv_with_doi)} 条")

    if arxiv_without_doi:
        warnings.append(f"发现 {len(arxiv_without_doi)} 条arXiv引用无DOI（可能未正式发表） / Found {len(arxiv_without_doi)} arXiv references without DOI (may not be formally published)")
        print(f"⚠️  无DOI（可能未正式发表）: {len(arxiv_without_doi)} 条:")
        for ref in arxiv_without_doi[:10]:
            print(f"   - {ref['ref_num']} Page {ref['page']}: arXiv:{ref['arxiv_id'][:30]}")
        if len(arxiv_without_doi) > 10:
            print(f"   ... 还有 {len(arxiv_without_doi) - 10} 条省略")
    else:
        print("✅ 所有arXiv引用均有DOI")

    return {
        'total_arxiv': len(arxiv_refs),
        'with_doi': len(arxiv_with_doi),
        'without_doi': len(arxiv_without_doi),
        'arxiv_refs': arxiv_refs,
        'without_doi_list': arxiv_without_doi,
        'warnings': warnings
    }
