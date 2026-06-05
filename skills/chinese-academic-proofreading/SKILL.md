---
name: chinese-academic-proofreading
description: 中文学术论文行文校对技能。用于中文论文、教改论文、学位论文、会议论文、期刊论文、报告或评审稿的错别字、漏字、多字、标点、病句、口语化表达、宣传腔、强断言、逻辑衔接、术语一致性、英文术语缺少中文对应和学术表达规范检查；当用户要求中文论文润色、行文校对、查错别字、去口语化、改成学术表达、检查宣传式表述、检查英文缩写/工具名是否有中文全称、生成校对清单、生成可读HTML校对报告，或希望配合docx生成修订版时使用。该技能输出机器可读Markdown和人类可读HTML，并可在需要编辑Word时配合 minimax-docx。
---

# Chinese Academic Proofreading

## Overview

Use this skill to proofread Chinese academic writing. It focuses on language and scholarly expression, not on judging the research contribution.

Default deliverables:

- A machine-readable Markdown proofreading report.
- A self-contained human-readable HTML report.

If the user asks to modify a `.docx` directly, use `/Users/yylonly/.agents/skills/minimax-docx/SKILL.md` after producing the proofreading plan.

## Input

Accept:

- PDF, DOCX, Markdown, TXT, HTML, or pasted Chinese text.
- A folder of papers or reports.
- Existing review reports whose writing needs polishing.

For long papers, proofread by sections and prioritize:

- title, abstract, keywords;
- introduction and contribution paragraphs;
- method/experiment/result/conclusion sections;
- reviewer-facing comments or decision text;
- paragraphs flagged by a review as having writing or presentation issues.

## Workflow

### 1. Extract Text and Preserve Context

Extract text with available PDF/DOCX/text tooling. Preserve:

- file path;
- title and section headings;
- page number or section location when available;
- original sentence or short paragraph around each issue.

Do not silently rewrite the whole paper unless the user asks for a revised manuscript. Prefer a targeted report first.

### 2. Classify Issues

Use these categories:

- `错别字/漏字/多字`: typos, duplicated words, missing words, OCR/extraction artifacts.
- `标点与格式`: Chinese/English punctuation mismatch, spacing around English terms, inconsistent numbering, table/figure caption wording.
- `病句与搭配`: ungrammatical wording, awkward collocation, unclear subject, broken sentence structure.
- `口语化表达`: informal, chatty, colloquial, or classroom-speaking style.
- `宣传腔/空泛表述`: slogan-like language, excessive praise, vague claims such as “显著提升”“效果良好”“广泛认可” without evidence.
- `强断言与证据不匹配`: claims stronger than the data support.
- `逻辑衔接`: unclear causal relation, missing transition, repeated or misplaced information.
- `术语一致性`: inconsistent translations or names, such as AI助教/智能助教/教学智能体 when they refer to the same object.
- `英文术语中文对应`: English acronyms, tool names, framework names, or technical terms that appear without a Chinese full name, Chinese explanation, or functional description when the expected audience is Chinese.
- `学术表达优化`: sentence can be more concise, precise, or formal.

### 3. Edit Conservatively

For each issue, provide:

- location;
- issue type;
- original text;
- problem explanation;
- suggested revision;
- confidence: high | medium | low.

Rules:

- Do not change technical meaning.
- Do not strengthen claims. If evidence is weak, downgrade the wording.
- Preserve domain terms and author intent.
- When a sentence may be correct but awkward, mark it as `学术表达优化`, not `错别字`.
- If the original sentence is ambiguous, suggest a conservative revision and note the assumption.
- Avoid over-editing names, references, equations, code, URLs, or quoted material.

### 3.1 Check English Terms and Chinese Counterparts

For Chinese academic papers, explicitly check English-only terms.

Flag an item when:

- an English acronym first appears without Chinese full name, such as `LLM`, `API`, `MCP`;
- an English tool/framework/library name appears without a functional explanation, such as `FAISS`, `Agno`, `GuideLM`;
- a paper mixes English and Chinese names for the same concept without a clear first definition, such as `Agent`, `智能体`, `教学智能体`, `智能助教`;
- figure/table labels or system diagrams contain English-only labels that a Chinese education-paper reader may not understand.

Do not flag:

- standard programming language names such as Java, Python, C, SQL when they are simply names;
- standard error abbreviations that are immediately explained, such as AC/WA/CE/TLE;
- email addresses, URLs, package identifiers, code variables, equations, or references;
- proper nouns where translating would be misleading, unless a short functional note would help.

Common patterns:

- `AI助教` -> first use `人工智能（AI）助教`, then `AI助教`.
- `LLM` -> `大语言模型（LLM）`.
- `API函数签名` -> `应用程序编程接口（API）函数签名`.
- `Agent整体系统架构` -> `教学智能体（Agent）整体系统架构`.
- `MCP工具` -> `模型上下文协议（MCP）工具`, or explain the tool's function if the protocol name is not intended.
- `Top-K相关知识点` -> `排名前K个（Top-K）相关知识点`.
- `FAISS向量索引空间` -> `FAISS向量检索库的索引空间` or add the full English expansion if useful.

### 4. Common Academic Rewrite Patterns

Use these patterns when appropriate:

- “效果显著” -> “结果显示……有所改善” unless statistical significance is reported.
- “极大提升/大幅提高” -> “提升/改善” or give the measured amount.
- “广泛认可/普遍认为” -> “问卷反馈显示/部分学生反馈” with sample details.
- “很好地解决了” -> “在一定程度上缓解了/支持了”.
- “推动智能教学模式升级” -> “为智能教学模式改进提供了参考”.
- “本文创新性地提出” -> “本文提出” unless novelty is externally supported.
- “大量实验表明” -> “实验结果表明” unless many experiments are actually described.
- “我们” -> “本文/研究团队/课程团队” in formal prose.
- “搞定/很厉害/不爱听/查查资料” -> replace with formal equivalents.
- “此现象说明” -> “这一结果提示” when the evidence is small-sample or descriptive.
- “更少/更高/更稳定” -> “较少/较高/较稳定” when writing formal comparative claims.

### 5. Output Markdown

Use this structure:

```markdown
# 中文学术论文行文校对报告

## 元数据

- 文件: ...
- 校对时间: ...
- 文档类型: paper | thesis | review | report | unknown
- 校对范围: full | partial | selected sections

## 总体判断

- 主要问题: ...
- 行文成熟度: 高 | 中 | 低
- 建议处理方式: 小修 | 中修 | 大修

## 校对问题清单

| 位置 | 类型 | 原文 | 建议修改 | 说明 | 置信度 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 英文术语中文对应检查

| 位置 | 原文 | 建议修改 | 说明 | 置信度 |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 重点段落改写

### 位置/章节

原文：
> ...

建议：
> ...

## 可直接替换的修改片段

1. ...

## 需作者确认的问题

1. ...
```

Keep quotations short. Do not reproduce large portions of copyrighted papers.

### HTML

Create a self-contained HTML report next to the Markdown file.

Include:

- title and metadata;
- issue summary cards by type;
- a table of issues;
- an English-term Chinese-counterpart table when such issues exist;
- highlighted before/after examples;
- a section for author-confirmation questions.

Do not use external network assets.

### DOCX Revision

If asked to create a revised Word document:

1. Produce the proofreading report first.
2. Use `minimax-docx` for `.docx` editing.
3. Preserve the original file by writing a new file such as `<name>_proofread.docx`.
4. For uncertain edits, either leave comments or list them in the report instead of silently changing the document.

## Validation

Before reporting completion:

```bash
python3 - <<'PY'
from pathlib import Path
out = Path("<output_dir>")
for p in out.glob("*proofread*.md"):
    text = p.read_text(errors="ignore")
    assert "校对问题清单" in text and "总体判断" in text
for p in out.glob("*proofread*.html"):
    text = p.read_text(errors="ignore")
    assert "校对问题清单" in text or "Issue" in text
    assert "http://" not in text and "https://" not in text
print("Chinese academic proofreading artifacts validated")
PY
```

When an English-term check is requested or relevant, also validate:

```bash
python3 - <<'PY'
from pathlib import Path
out = Path("<output_dir>")
for p in out.glob("*proofread*.md"):
    text = p.read_text(errors="ignore")
    assert "英文术语中文对应检查" in text
for p in out.glob("*proofread*.html"):
    text = p.read_text(errors="ignore")
    assert "英文术语中文对应检查" in text
print("English-term counterpart checks validated")
PY
```

## Evidence Discipline

- Separate confirmed errors from style suggestions.
- Do not invent grammar problems.
- Do not convert every long sentence into short sentences if the original academic style is acceptable.
- Mark OCR or extraction artifacts as uncertain when they may not exist in the original PDF.
- Keep issue counts synchronized after adding a new issue category; update summary tables and HTML badges.
- When the task is a review report, preserve the reviewer's decision and scoring unless the user explicitly asks to change them.
