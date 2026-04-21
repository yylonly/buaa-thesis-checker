---
name: buaa-thesis-format-checking
description: 北航硕士论文格式自动化检测工具。用于检测论文是否符合北京航空航天大学学位论文书写规范。触发场景：用户提到"检测论文"、"格式检查"、"thesis audit"、"论文规范"时。功能：空白页面、占位符、章节连续性、过渡段、URL位置、中英文摘要、文本对齐、字体字号、行间距等14项检测。
compatibility: Requires Python 3.10+ with pypdf and pymupdf installed.
metadata:
  author: yylonly
  version: "1.1"
allowed-tools: Bash python Read TaskCreate TaskUpdate TaskList
---

# BUAA Thesis Format Checking Skill

## When to Use

Activate when user mentions: "检测论文"、"格式检查"、"thesis audit"、"论文规范"

## Quick Start

```bash
python3 <skill_path>/scripts/thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]
```

## Workflow

1. **Extract PDF text** — `thesis_audit_script.py --step1 <pdf_path>`
2. **Run 14 format checks** — `thesis_audit_script.py --step2 <text_path> --type cn`
3. **Generate JSON report** — `thesis_audit_script.py --step3-json <results_path> <pdf_path>`
4. **Verify report accuracy** — Agent reviews JSON vs original PDF
5. **Generate HTML report** — `thesis_audit_script.py --step3-html <results_path> <pdf_path>` (after verification passed)

## Detection Items

| # | Item | Type |
|---|------|------|
| 1 | Blank pages | Warning |
| 2 | Placeholders (XXX, ****, TODO) | Warning |
| 3 | Chapter continuity (1-5) | Pass/Fail |
| 4 | Low content pages (<20% avg) | Warning |
| 5 | Incomplete markers ("to be continued") | Warning |
| 6 | Transition paragraphs | Warning |
| 7 | URLs in body (should be in footnotes) | Fail |
| 8 | arXiv without DOI | Warning |
| 9 | Abstract existence + word count | Warning |
| 10 | Text alignment (justify) | Warning |
| 11 | Font detection | Warning |
| 12 | Font size detection | Warning |
| 13 | Line spacing (1.5x for Chinese) | Warning |
| 14 | Page margins + page numbers | Warning |

## Known False Positives

- "攻读硕士学位期间取得的研究成果 - 无" is correct format, not a problem
- Table pages use left-align, which is correct
- Cover page has naturally low content

## Dependencies

```bash
pip install pypdf pymupdf
```

## References

- Format standard: `references/Chapter-3-Writing-Standard-and-Printing-Styles.md`
