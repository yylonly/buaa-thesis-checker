---
name: buaa-thesis-format-checking
description: 北航学位论文格式自动化检测工具。用于检测论文是否符合北京航空航天大学学位论文书写规范，支持硕士、博士及本科毕业设计论文。触发场景：用户提到"检测论文"、"格式检查"、"thesis audit"、"论文规范"、"论文格式"时自动触发。功能：空白页面、占位符、章节连续性、过渡段、URL位置、中英文摘要（中英文关键词）、文本对齐、字体字号、行间距、图表间距等14项检测。注意：行内文字间距过大/视觉空洞问题无法自动检测，必须人工核对PDF。
metadata:
  author: yylonly
  version: "1.2"
allowed-tools: Bash python Read TaskCreate TaskUpdate TaskList
---

# BUAA Thesis Format Checking Skill

## When to Use

Activate when user mentions: "检测论文"、"格式检查"、"thesis audit"、"论文规范"

## Quick Start

```bash
python3 <skill_path>/scripts/thesis_audit_script.py --step1 <pdf_path> <output_dir>
python3 <skill_path>/scripts/thesis_audit_script.py --step2 <output_dir>/thesis_text_extracted.json --type cn
python3 <skill_path>/scripts/thesis_audit_script.py --step3-json <output_dir>/thesis_check_results.json <pdf_path> <output_dir>
```

Use the stepwise workflow for thesis review. It preserves intermediate artifacts and avoids cross-talk during parallel runs.

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
- Title, authorization, declaration, abstract divider, table of contents, symbol table, chapter-ending, and figure/table-heavy pages often have naturally low text density
- Font,字号,line spacing, margins, alignment, and figure spacing are candidate findings only; cite them as confirmed problems only after PDF or source-layout verification

## Cannot Auto-Detect (Manual Check Required)

以下问题无法通过文本提取自动检测，**必须人工核对PDF**：
- **行内文字间距过大/视觉空洞**：正文页面文字两端对齐但内部有明显缝隙，呈现"锯齿状"空白区域
- **部分过渡段缺失**：仅检测二级与三级标题之间，三级与四级之间未覆盖
- **图表编号缺失或格式错误**：仅检测间距，不检测编号

## Operational Notes

- Use a dedicated output directory for every PDF, especially in parallel review.
- If a PDF path with Chinese characters, spaces, or punctuation causes report generation failure, create an ASCII symlink/copy in the output directory and rerun against it.
- If HTML generation fails after checks have completed, keep `thesis_text_extracted.json` and `thesis_check_results.json`; downstream review may continue from these artifacts.
- `--step2` writes `thesis_check_results.json` beside the `thesis_text_extracted.json` input, which makes parallel runs safer.
- Do not treat this tool as a final authority. Its findings are candidates for agent/manual verification.

## Dependencies

Requires Python 3.10+ with `pypdf` and `pymupdf`.

```bash
python3 -m pip install pypdf pymupdf
```

## References

- Format standard: `references/Chapter-3-Writing-Standard-and-Printing-Styles.md`
