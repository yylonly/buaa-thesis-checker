---
name: icse-seet-review
description: ICSE SEET软件工程教育与培训论文评审技能。用于评审Software Engineering Education and Training教育类论文、ICSE SEET投稿或类似软件工程教育研究/经验/工具论文；当用户要求SEET review、教育类顶会论文评审、按Relevance/Significance/Soundness/Verifiability/Presentation标准写评审意见、分析教育研究论文是否达到ICSE SEET标准、生成机器可读Markdown和给人看的图文并茂HTML时使用。该技能强调先判定论文类型，再按ICSE SEET对应类别标准做证据化评审，将主要不足从逐项标准风险中提炼，并分章输出主要优点、主要不足、修改建议、正式评语、评分/结果和可视化报告。
---

# ICSE SEET Review

## Overview

Use this skill to review software engineering education and training papers in the style of the ICSE SEET track. It is for peer-review style evaluation, not degree-thesis evaluation.

Default to ICSE SEET 2026 criteria when the user does not name another year. If the target year matters or the user asks for the latest criteria, verify the official ICSE SEET call for papers online before writing the review.

Deliver both:

- A machine-readable Markdown review.
- A self-contained human-facing HTML report with compact visual summaries.

## Required Input

Require at least one paper PDF, DOCX, arXiv URL, ACM/IEEE page, or extracted paper text.

Ask only when essential:

- Target venue/year if not ICSE SEET or if a specific call is required.
- Paper category if the paper itself does not make it inferable.

Infer the paper category from title, abstract, contribution framing, and venue metadata when possible:

- Research Paper
- Experience Report
- Idea Paper
- Tool Paper
- Extended Abstract

## Core Criteria

### Research Paper

Evaluate against:

- Relevance: fit to software engineering education and training.
- Significance: importance, originality, and educational or research impact.
- Soundness: appropriateness and rigor of research questions, method, data, analysis, and conclusions.
- Verifiability: transparency, reproducibility, artifacts, instruments, codebooks, datasets, prompts, protocols, and threat analysis.
- Presentation: clarity, organization, related work positioning, figures/tables, and writing quality.

### Experience Report

Evaluate against:

- Relevance: fit to software engineering education/training practice.
- Significance: importance of the educational setting, intervention, and outcomes.
- Actionability: whether other instructors, programs, or institutions can reuse the lessons.
- Lessons: whether lessons are specific, evidence-backed, and transferable.
- Presentation: clarity and professional exposition.

### Idea Paper

Evaluate against:

- Relevance
- Significance
- Soundness of the proposed evaluation strategy
- Presentation

### Tool Paper

Evaluate against:

- Relevance
- Significance
- Tool maturity and educational workflow integration
- Evidence of educational impact or a credible evaluation path
- Availability or verifiability of tool behavior
- Presentation

### Extended Abstract

Evaluate against:

- Relevance
- Significance
- Potential to stimulate SEET discussion
- Presentation

## Review Workflow

### 0. Prepare Workspace

For each paper, create a dedicated output directory. When evaluating multiple papers in parallel, give each worker an exclusive directory and never share intermediate filenames.

Recommended layout:

```text
seet_reviews/<paper_slug>/
  extracted/
  icse_seet_review_YYYYMMDD_HHMMSS.md
  icse_seet_review_YYYYMMDD_HHMMSS.html
```

If the input path contains spaces, non-ASCII characters, or punctuation and a PDF/DOCX tool fails unexpectedly, create an ASCII symlink or copy inside the paper-specific output directory and rerun against that path. Preserve the original path in report metadata.

### 1. Extract and Triage the Paper

Use available PDF/DOCX tooling to extract text, metadata, figures, tables, and references. Use `/Users/yylonly/.agents/skills/minimax-pdf/SKILL.md` for visually sensitive PDF inspection when needed.

Capture:

- Title, authors if needed, paper category, research context, target learners/instructors, course/program setting.
- Author names and affiliations when present in the paper. If extraction cannot find them, mark them as not identified rather than guessing.
- Research questions, intervention/tool/method, data sources, participants, tasks, instruments, measurements, analysis method.
- Main claims and evidence.
- Threats to validity, ethics/consent/privacy, artifacts, replication package, supplementary materials.

Do not rely only on the abstract. Confirm claims in the method, results, discussion, and limitations sections.

### 2. Build the SEET Evidence Map

Create a compact evidence map before writing the review:

```text
SEET problem/context -> educational or training contribution -> study/evidence -> claims -> limitations
```

For each main claim, trace:

- What educational problem does it address?
- What is new or valuable for SE education/training?
- What evidence supports it?
- What boundary conditions limit the claim?
- What would an instructor/researcher be able to reuse?

Treat technical novelty as supportive, not sufficient. In SEET, the contribution must advance software engineering education, training practice, learning science, assessment, or instructor/student workflows.

### 3. Apply Category-Specific Standards

Use the inferred category’s criteria. Avoid forcing Research Paper standards onto Experience Reports and Tool Papers.

Look for these evidence patterns:

- Research Paper: explicit research questions, justified method, credible sample/data, analysis aligned with RQs, validity threats, relation to education literature, reproducibility details.
- Experience Report: real setting, intervention timeline, concrete observations, failures and tradeoffs, actionable lessons, transfer conditions.
- Tool Paper: actual educational workflow, user roles, deployment or realistic scenario, comparison to existing tools, availability/demo, evidence of learning/teaching value.
- Idea Paper: clear motivating gap, coherent proposed intervention, plausible evaluation plan, early evidence if claimed.

### 4. Calibrate Strengths and Weaknesses

Write strengths only when supported by paper evidence. Typical accepted SEET papers make the criteria concrete by:

- Grounding relevance in an authentic SE education setting such as programming courses, modeling/UML assessment, capstone projects, software architecture, DevOps, teamwork, GenAI use, or informal learning spaces.
- Showing significance through a widely felt instructional or learning pain point, not merely a new software feature.
- Demonstrating soundness through survey design, thematic analysis, manual annotation, longitudinal/retrospective course data, controlled comparison, mixed methods, or carefully documented experience evidence.
- Supporting verifiability through datasets, prompts, rubrics, codebooks, assignment materials, tools, replication packages, or detailed protocols.
- Translating findings into lessons or design implications that other SE educators can adapt.

Common concerns:

- Contribution is an AI/tool novelty with weak connection to learning or SE education outcomes.
- Claims exceed evidence, especially with small samples or one-off classroom deployments.
- Prior work in computing education or SE education is too thin.
- Evaluation lacks baseline, comparison, triangulation, statistical/qualitative rigor, or validity analysis.
- Artifacts, prompts, rubrics, data, or analysis code are unavailable without explanation.
- Ethical handling of student data, consent, privacy, or grading impact is unclear.
- Lessons are generic rather than actionable.

When writing the final review, split weaknesses and advice:

- `主要不足`: derive these primarily from the `主要风险` column in the standards table. They should describe what is weak, missing, unclear, overclaimed, or hard to verify.
- `修改建议`: make these actionable responses to the weaknesses. Each suggestion should tell the author what to add, revise, measure, release, or clarify.

Do not merge `主要不足` and `修改建议` into one section unless the user explicitly asks for a compact review.

Presentation and writing quality are part of the review:

- Assess structure, clarity, contribution boundary, figure/table captions, statistics wording, citation adequacy, and whether the prose is analytical rather than promotional.
- Fold writing and format issues into `主要优点` or `主要不足`; do not create a separate writing-quality section unless the user asks.
- A paper with much implementation or teaching activity can still be weak if the writing is slogan-like, the evidence chain is unclear, or the figures/tables do not support the claims.

### 5. Produce Review Judgment

Provide a reviewer-style recommendation only when the user asks for it or the context implies a conference review. Use a cautious scale:

- Strong Accept
- Accept
- Weak Accept
- Borderline
- Weak Reject
- Reject
- Strong Reject

Always include confidence:

- High: paper and criteria are available; review is evidence-grounded.
- Medium: paper is available but some artifacts or venue details are missing.
- Low: only abstract/metadata or partial text is available.

Do not overstate acceptance odds. A review is a reasoned assessment, not a prediction.

If the user asks for a numeric Chinese review score, use this scale:

- 5（很好）
- 4（好）
- 3（有些好）
- 2（一般）
- 1（不好）
- -1（非常不好）

Use category-sensitive calibration:

- `4（好）`: solid fit and contribution for the paper type, with meaningful evidence or a mature, useful design, though not flawless.
- `3（有些好）`: relevant and potentially useful, but evidence, novelty, evaluation plan, or presentation is incomplete; usually a weak accept/borderline pass.
- `2（一般）`: relevant but not yet mature enough for acceptance because evidence, actionability, writing, or verification is too weak.
- `1（不好）` or `-1（非常不好）`: serious mismatch, unsupported claims, poor presentation, or lack of credible contribution.

For `审核结果`, default to:

- `审核通过` for 3, 4, or 5.
- `审核不通过` for 2, 1, or -1.

The user may impose a different pass/fail distribution; if so, state the changed decision rule in the report metadata or summary.

### 6. Keep the Formal Author Comment Narrow

`给作者的正式评语` should summarize what the paper mainly does:

- the educational problem or setting;
- the proposed teaching model, intervention, tool, or reform;
- the evidence or materials the paper uses, if central;
- the paper's intended contribution.

Do not use this section for detailed criticism, pass/fail justification, or revision instructions. Put those in `主要不足`, `修改建议`, and `摘要判断`.

## Output Requirements

### Markdown

Create a concise, parseable Markdown file:

```markdown
# ICSE SEET论文评审意见

## 元数据

- 论文文件: ...
- 作者: ...
- 作者单位: ...
- 目标标准: ICSE SEET YYYY
- 论文类别: Research Paper | Experience Report | Idea Paper | Tool Paper | Extended Abstract
- 评审时间: ...
- 证据完整性: full | partial | abstract-only

## 摘要判断

- 推荐意见: ...
- 审核评分: 5（很好）|4（好）|3（有些好）|2（一般）|1（不好）|-1（非常不好）
- 审核结果: 审核通过|审核不通过
- 评审信心: ...
- 核心理由: ...

## 标准逐项评价

| 标准 | 评价 | 关键证据 | 主要风险 |
|---|---|---|---|
| Relevance | ... | ... | ... |
| Significance | ... | ... | ... |
| Soundness/Actionability/etc. | ... | ... | ... |
| Verifiability/Lessons/etc. | ... | ... | ... |
| Presentation | ... | ... | ... |

## 主要优点

1. ...

## 主要不足

1. ...

## 修改建议

1. ...

## 给作者的正式评语

...

## 证据摘要

- 教育场景与对象: ...
- 贡献-证据链: ...
- 可复现/可迁移材料: ...
- 需要人工复核或外部材料: ...
```

### HTML

Create a self-contained HTML report next to the Markdown file.

Include:

- Title area with paper title, authors if available, affiliations if available, category, target standard, recommendation, numeric score/result when used, and confidence.
- Criteria dashboard with visual status for each criterion.
- Prominent human-readable sections:
  - `主要优点`
  - `主要不足`
  - `修改建议`
- A compact evidence diagram for `教育问题 -> 贡献 -> 方法/证据 -> 结论边界 -> 可迁移启示`.
- A printable formal review section for `给作者的正式评语`.

HTML design:

- Use embedded CSS only; no external network assets.
- Use academic, readable styling with high contrast and print-friendly layout.
- Use inline SVG or CSS-only visuals for criteria bars, evidence maps, or badges.
- Do not fabricate numerical scores unless the paper evidence supports them; categorical levels such as strong / adequate / weak / uncertain are preferred.

Before reporting completion, validate:

```bash
python3 - <<'PY'
from pathlib import Path
out = Path("<output_dir>")
for p in out.glob("icse_seet_review_*.md"):
    text = p.read_text(errors="ignore")
    assert "标准逐项评价" in text and "主要不足" in text and "修改建议" in text
for p in out.glob("icse_seet_review_*.html"):
    text = p.read_text(errors="ignore")
    assert "主要优点" in text and "主要不足" in text and "修改建议" in text
    assert "http://" not in text and "https://" not in text
print("ICSE SEET review artifacts validated")
PY
```

### Multi-paper Summary

When reviewing multiple papers, also create an index HTML and Markdown in the batch output directory.

The index must include:

- paper title;
- authors and affiliations when available;
- inferred paper category;
- recommendation, score, review result, and confidence;
- one concise basis sentence;
- links to each paper's HTML and Markdown report.

Use absolute local links when the output is meant for the Codex desktop app or local browser preview.

## Evidence Discipline

- Cite page/section evidence when available.
- Separate paper evidence from reviewer inference.
- Do not penalize an Experience Report for lacking a full controlled study if it provides clear, transferable lessons.
- Do not praise a Tool Paper only for implementation effort; judge educational use and evidence.
- Do not treat GenAI use as inherently novel. Ask what it changes for SE learning, assessment, feedback, or instructor workload.
- If only partial text is available, mark unsupported criteria as uncertain instead of inventing findings.
- If using current ICSE criteria or accepted-paper examples, include source URLs in the Markdown evidence section.
