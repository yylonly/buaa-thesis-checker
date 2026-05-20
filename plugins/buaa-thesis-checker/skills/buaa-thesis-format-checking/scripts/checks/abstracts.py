"""中英文摘要检测"""
import re
from typing import List, Dict


def check_abstracts(content_by_page: List[Dict]) -> Dict:
    """
    检查中英文摘要的存在性和字数

    Returns:
        Dict with keys: result dict, warnings
    """
    result = {
        'chinese_abstract_found': False,
        'english_abstract_found': False,
        'chinese_keywords_found': False,
        'english_keywords_found': False,
        'chinese_abstract_pages': [],
        'english_abstract_pages': [],
        'chinese_word_count': 0,
        'english_word_count': 0,
        'chinese_keywords': [],
        'english_keywords': []
    }

    chinese_abstract_patterns = ['摘  要', '摘要', '中文摘要', '摘 要']
    english_abstract_patterns = ['Abstract', 'ABSTRACT']
    chinese_keyword_patterns = ['关键词', '关键字']
    english_keyword_patterns = ['Keywords', 'KEYWORDS', 'Index Terms']

    abstract_section_pages = set()
    chinese_abstract_text = ""
    english_abstract_text = ""
    in_chinese_abstract = False
    in_english_abstract = False

    for content in content_by_page[:15]:
        if not content['text']:
            continue
        text = content['text']

        for pattern in chinese_abstract_patterns:
            if pattern in text:
                in_chinese_abstract = True
                abstract_section_pages.add(content['page'])
                result['chinese_abstract_found'] = True
                result['chinese_abstract_pages'].append(content['page'])
                break

        for pattern in english_abstract_patterns:
            if pattern in text and 'Table of Contents' not in text:
                in_english_abstract = True
                abstract_section_pages.add(content['page'])
                result['english_abstract_found'] = True
                result['english_abstract_pages'].append(content['page'])
                break

        if in_chinese_abstract:
            for pattern in chinese_keyword_patterns:
                if pattern in text:
                    result['chinese_keywords_found'] = True
                    kw_match = re.search(rf'{pattern}[:：]\s*([^\n]+)', text)
                    if kw_match:
                        result['chinese_keywords'] = [k.strip() for k in kw_match.group(1).split(',')]
                    break

        if in_english_abstract:
            for pattern in english_keyword_patterns:
                if pattern in text:
                    result['english_keywords_found'] = True
                    kw_match = re.search(rf'{pattern}[:]\s*([^\n]+)', text)
                    if kw_match:
                        result['english_keywords'] = [k.strip().rstrip('.') for k in kw_match.group(1).split(',')]
                    break

        if in_chinese_abstract and content['text']:
            if 'Abstract' in text and 'Keywords' not in chinese_keyword_patterns:
                in_chinese_abstract = False
            elif '目  录' in text or 'Contents' in text or '第1章' in text:
                in_chinese_abstract = False
            else:
                chinese_abstract_text += " " + text

        if in_english_abstract and content['text']:
            if 'Acknowledgements' in text or 'Acknowledgement' in text:
                in_english_abstract = False
            elif 'References' in text or '第1章' in text:
                in_english_abstract = False
            else:
                english_abstract_text += " " + text

    if chinese_abstract_text:
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', chinese_abstract_text))
        result['chinese_word_count'] = chinese_chars

    if english_abstract_text:
        english_words = english_abstract_text.split()
        result['english_word_count'] = len(english_words)

    warnings = []

    print(f"\n   中文摘要:")
    if result['chinese_abstract_found']:
        print(f"      ✅ 找到 (页码: {result['chinese_abstract_pages']})")
        print(f"      字数: 约 {result['chinese_word_count']} 字 (规范要求≥500字)")
        if result['chinese_keywords_found']:
            print(f"      关键词: {result['chinese_keywords']}")
        else:
            print(f"      ⚠️ 未找到中文关键词")
        if result['chinese_word_count'] < 400:
            warnings.append(f"中文摘要字数偏少（约{result['chinese_word_count']}字，建议≥500字） / Chinese abstract word count low (~{result['chinese_word_count']} chars, recommended ≥500)")
    else:
        print(f"      ❌ 未找到中文摘要")
        warnings.append("未找到中文摘要 / Chinese abstract not found")

    print(f"\n   英文摘要:")
    if result['english_abstract_found']:
        print(f"      ✅ 找到 (页码: {result['english_abstract_pages']})")
        print(f"      单词数: 约 {result['english_word_count']} 词")
        if result['english_keywords_found']:
            print(f"      Keywords: {result['english_keywords']}")
        else:
            print(f"      ⚠️ 未找到英文关键词")
    else:
        print(f"      ❌ 未找到英文摘要")
        warnings.append("未找到英文摘要 / English abstract not found")

    return {
        'result': result,
        'warnings': warnings
    }
