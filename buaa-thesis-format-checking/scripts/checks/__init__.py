"""检测模块集合"""
from .blank_pages import check_blank_pages
from .placeholders import check_placeholders
from .section_continuity import check_section_continuity
from .low_content_pages import check_low_content_pages
from .incomplete_content import check_incomplete_content
from .urls_in_body import check_urls_in_body
from .arxiv_without_doi import check_arxiv_without_doi
from .abstracts import check_abstracts
from .text_alignment import check_text_alignment
from .figure_pages import check_figure_pages
from .transition_paragraphs import check_transition_paragraphs
from .font_line_spacing import check_font_and_spacing
from .fonts import check_fonts

__all__ = [
    'check_blank_pages',
    'check_placeholders',
    'check_section_continuity',
    'check_low_content_pages',
    'check_incomplete_content',
    'check_urls_in_body',
    'check_arxiv_without_doi',
    'check_abstracts',
    'check_text_alignment',
    'check_figure_pages',
    'check_transition_paragraphs',
    'check_font_and_spacing',
    'check_fonts',
]
