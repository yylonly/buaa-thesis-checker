---
name: buaa-thesis-checking
description: 北航学位论文综合评审技能。用于对北京航空航天大学硕士或博士论文PDF进行“格式检查 + 内容审核 + 学术评语生成 + Markdown/HTML报告交付”的串联评审；当用户要求论文评阅意见、学术评语、论文不足与修改建议、北航论文综合检查、thesis checking、论文格式与内容同时审核、生成机器可读Markdown和给人看的图文并茂HTML时使用。该技能必须先使用 buaa-thesis-format-checking，再核对其可能的误报，随后使用 buaa-thesis-content-checking，最后生成两块核心中文评语并同时交付Markdown与HTML。
---

# BUAA Thesis Checking

## Overview

Use this skill to compose a final thesis review opinion from two existing BUAA skills:

1. `buaa-thesis-format-checking`
2. `buaa-thesis-content-checking`

The final review content must contain exactly two substantive blocks:

1. 学术评语
2. 不足、问题与修改意见

Deliver both:

- A machine-readable Markdown report.
- A human-facing HTML report with polished visual structure and simple evidence graphics.

Do not expose long intermediate reports unless the user explicitly asks for them.

## Required Input

Require a thesis PDF path or an accessible thesis PDF artifact. If the user provides DOCX instead of PDF, convert or ask for a PDF only when conversion is not feasible.

Ask for the thesis type only when needed for format checking and not inferable:

- Chinese thesis: `--type cn`
- English thesis: `--type en`

Default to `cn` for Chinese-language BUAA theses.

## Workflow

### 0. Prepare a Safe Workspace

For each thesis, create a dedicated output directory. When evaluating multiple PDFs in parallel, give each worker an exclusive directory and never share intermediate filenames across workers.

Recommended layout:

```text
reviews/<paper_id_or_slug>/
  format_check/
  content_check/
  buaa_thesis_review_YYYYMMDD_HHMMSS.md
  buaa_thesis_review_YYYYMMDD_HHMMSS.html
```

If the PDF path contains spaces, non-ASCII characters, or punctuation and a script fails unexpectedly, create an ASCII symlink or copy inside the paper-specific output directory and rerun against that path. Preserve the original PDF path in the final report metadata.

### 1. Run Format Checking First

Use `/Users/yylonly/.agents/skills/buaa-thesis-format-checking/SKILL.md`.

Typical command:

```bash
python3 /Users/yylonly/.agents/skills/buaa-thesis-format-checking/scripts/thesis_audit_script.py --step1 <pdf_path> <output_dir>/format_check
python3 /Users/yylonly/.agents/skills/buaa-thesis-format-checking/scripts/thesis_audit_script.py --step2 <output_dir>/format_check/thesis_text_extracted.json --type cn
python3 /Users/yylonly/.agents/skills/buaa-thesis-format-checking/scripts/thesis_audit_script.py --step3-json <output_dir>/format_check/thesis_check_results.json <pdf_path> <output_dir>/format_check
```

The all-in-one command is acceptable for quick checks:

```bash
python3 /Users/yylonly/.agents/skills/buaa-thesis-format-checking/scripts/thesis_audit_script.py <pdf_path> <output_dir>/format_check --type cn
```

Prefer the stepwise commands for thesis review because they preserve reusable JSON artifacts and make manual verification easier.

### 2. Verify Format Findings Before Using Them

Treat format-checking output as suspicious until verified. The format checker is known to hallucinate or over-report.

For every format issue that may appear in the final review:

- Reopen the cited page or extracted text around the reported location.
- Confirm the issue in the original PDF when possible.
- Downgrade uncertain findings to cautious wording, such as “建议进一步核查”.
- Exclude findings that match known false positives.

Known false positives:

- “攻读硕士学位期间取得的研究成果 - 无” is acceptable and should not be criticized.
- Table pages may be left-aligned and should not be criticized solely for alignment.
- Cover, title, authorization, declaration, abstract divider, and other front-matter pages may have naturally low text density.

Do not include exact font,字号,line-spacing, margin, or alignment criticism unless the PDF evidence is directly checked and the problem is visible or otherwise technically confirmed.

If the format script detects issues but fails while generating HTML/JSON reports, continue from any available console output and extracted JSON/text. State this limitation in metadata; do not block the content review.

### 3. Run Content Checking Second

Use `/Users/yylonly/.agents/skills/buaa-thesis-content-checking/SKILL.md`.

Typical commands:

```bash
python3 /Users/yylonly/.agents/skills/buaa-thesis-content-checking/scripts/check_deps.py --yes
python3 /Users/yylonly/.agents/skills/buaa-thesis-content-checking/scripts/paper_audit_script.py --step1 <pdf_path> <output_dir>/content_check
```

Then analyze the extracted thesis and generated artifacts according to the content-checking skill:

- Identify the core research problem, methods, experiments, and conclusions.
- Limit main contributions or innovations to at most three.
- Trace each claim through `problem -> method/new insight -> evidence`.
- Check whether claims are supported by experiments, theory, cases, data, or system implementation.
- Compare with baselines or prior work when the thesis makes performance or novelty claims.

If the content script cannot generate its full automatic report because an LLM SDK/API key is unavailable or a script fallback fails, use `content_check/paper_text_extracted.txt` as the authoritative extracted text and complete the analysis manually. Record the script limitation in `元数据` or `证据摘要`.

Use web/literature lookup only for targeted validation of novelty, venue, CCF level, or very recent references. Cite limitations when only partial external verification is feasible.

### 4. Synthesize Only Two Core Review Blocks

Write in the style of a formal academic degree-thesis review. Be specific enough to be useful, but do not produce a long checklist.

The core review text must include these two blocks and no extra substantive opinion sections:

#### 学术评语

Cover all of the following in one coherent paragraph or a few tightly connected paragraphs:

- 论文的理论意义或实用价值。
- 哪些内容属于论文的新见解、新方法、新系统、新实验发现或新应用。
- 论文的学术观点是否科学、严谨，论证是否充分。
- 论文工作的技术难度和工作量。
- 写作是否规范。 Only mention format issues verified in step 2.

Use balanced language. When evidence is strong, state it directly. When evidence is partial, use qualified language.

#### 不足、问题与修改意见

Cover the main actionable problems:

- Content limitations: unclear contribution boundary, insufficient baseline comparison, incomplete ablation, limited datasets/cases, weak threat analysis, missing error analysis, insufficient theory-to-experiment traceability.
- Format or writing problems: only include verified issues, or phrase as items needing further manual check.
- Revision advice: concrete, prioritized changes the author can make.

Avoid inventing unsupported flaws. If no serious issue is verified, state that only minor revisions are recommended.

### 5. Produce Markdown and HTML Deliverables

Create an output directory for the review artifacts. Use a deterministic naming pattern when possible:

```text
buaa_thesis_review_YYYYMMDD_HHMMSS.md
buaa_thesis_review_YYYYMMDD_HHMMSS.html
```

The Markdown file is for machine consumption and downstream editing. The HTML file is for human reading and should be visually polished.

#### Markdown Requirements

The Markdown must be concise and structured for parsing:

```markdown
# 北航学位论文综合评审意见

## 元数据

- 论文文件: ...
- 论文类型: cn|en
- 评审时间: ...
- 格式检查: 已执行，并已人工核对候选问题
- 内容审核: 已执行

## 学术评语

...

## 不足、问题与修改意见

...

## 证据摘要

- 新见解/贡献: ...
- 技术难度与工作量依据: ...
- 已核实的格式/写作问题: ...
- 不确定或需人工复核事项: ...
```

`学术评语` and `不足、问题与修改意见` remain the only two substantive review-opinion blocks. `元数据` and `证据摘要` are support sections for traceability, not extra评语.

#### HTML Requirements

The HTML must be self-contained and readable in a browser without external network assets. Use embedded CSS and, when useful, inline SVG or CSS-only visuals.

Include:

- Title area with thesis name if available, review date, and review scope.
- Two prominent content sections: `学术评语` and `不足、问题与修改意见`.
- A compact evidence dashboard showing:
  - format check status: executed / verified / uncertain items
  - content check status: problem-method-evidence traceability
  - contribution count, issue count, and revision priority count when available
- A simple visual such as an inline SVG flow diagram for `格式检查 -> 复核 -> 内容审核 -> 综合评语`, or a small bar/radar-style summary for contribution, rigor, workload, writing规范性. Keep visuals explanatory; do not fabricate scores unless the evidence supports them.
- Optional page thumbnails or extracted figures only when available from the PDF processing artifacts and clearly relevant. If no image artifacts exist, use clean inline diagrams instead of pretending images were extracted.

HTML design guidance:

- Use professional academic styling: restrained colors, high contrast, printable layout, readable Chinese font stack.
- Avoid decorative clutter. “图文并茂” means evidence diagrams, summary cards, and readable layout, not unsupported illustrations.
- Mark uncertain findings visually with a subdued “需复核” badge.
- Separate verified findings from unverified checker output.

Run a final local validation before reporting completion:

```bash
python3 - <<'PY'
from pathlib import Path
for p in Path("<output_dir>").glob("buaa_thesis_review_*.md"):
    text = p.read_text(errors="ignore")
    assert "学术评语" in text and "不足、问题与修改意见" in text
for p in Path("<output_dir>").glob("buaa_thesis_review_*.html"):
    text = p.read_text(errors="ignore")
    assert "学术评语" in text and "不足、问题与修改意见" in text
    assert "http://" not in text and "https://" not in text
print("review artifacts validated")
PY
```

#### Final User Response

After generating files, respond briefly with links to both artifacts and a short note that format findings were checked before inclusion.

## Evidence Discipline

- Never copy the format checker’s findings directly into the final review without verification.
- Treat every automated format issue as a candidate, not a conclusion.
- Do not claim a novelty point unless it is visible in the thesis text and connected to evidence.
- Do not claim “工作量大” only from page count. Use implementation scope, experiments, datasets, algorithms, case studies, or system modules as support.
- Do not judge academic rigor solely from writing style. Tie rigor to assumptions, method design, evaluation, baseline comparison, and conclusion boundaries.
- Preserve uncertainty: use “从现有材料看”, “建议补充说明”, or “仍需进一步核查” when evidence is incomplete.

## Parallel Review Pattern

When the user asks to review multiple theses, dispatch one worker per PDF only if the user explicitly authorizes multiple agents or parallel work. Assign each worker:

- the exact PDF path
- the exclusive output directory
- the two underlying skill paths
- the requirement to create Markdown and self-contained HTML
- the requirement to list created files and limitations

After workers finish, perform a parent-level validation over all final `.md` and `.html` files and summarize the artifact links.

## Output Template

```markdown
# 北航学位论文综合评审意见

## 元数据

- 论文文件: ...
- 评审时间: ...
- 输出文件: Markdown + HTML

## 学术评语

……

## 不足、问题与修改意见

……

## 证据摘要

- ……
```
