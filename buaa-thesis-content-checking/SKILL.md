---
name: buaa-thesis-content-checking
description: 学术论文内容审核工具。用于审核论文的主要贡献、方法创新性、实验评估及baseline对比。触发：用户提到"审核论文"、"论文评审"、"paper review"、"论文创新性"、"论文贡献"、"论文评估"、"review paper"、"audit paper"、"论文对比baseline"。核心：追溯关系图(P→I→E)、CCF顶会顶刊判断、贡献点数量约束(≤3个)。输出：Markdown + HTML格式中文英文审核报告。
compatibility: Requires Python 3.9+ with pdfplumber, PyMuPDF, and pypdf installed.
metadata:
  author: yylonly
  version: "1.2"
allowed-tools: Bash python Read TaskCreate TaskUpdate TaskList WebSearch Agent
---

# Paper Content Audit Skill

## When to Use

Activate when user mentions: "审核论文"、"论文评审"、"paper review"、"论文创新性"、"论文贡献"、"论文评估"、"review paper"、"audit paper"、"论文对比baseline"

## Quick Start

```bash
# Step 1: Check and install dependencies automatically
python3 <skill_path>/scripts/check_deps.py

# Step 2: Run PDF extraction and analysis
python3 <skill_path>/scripts/paper_audit_script.py --step1 <pdf_path> [output_dir]
```

## Pre-flight Dependency Check

**IMPORTANT:** Before running the script, always check that required packages are installed:

```bash
python3 -c "import pdfplumber; import fitz; from pypdf import PdfReader; print('All dependencies OK')"
```

If this fails, install dependencies with:

```bash
python3 -m pip install pymupdf pdfplumber pypdf --quiet
```

Or use the helper script:

```bash
python3 <skill_path>/scripts/check_deps.py
```

## Workflow

### Traceability Chain

```
主要问题 (P) → 方法创新 (I) → 评估验证 (E)
```

### Tasks

| Task | Description | Dependency |
|------|-------------|-------------|
| #1 | PDF text extraction | - |
| #2 | Reference investigation (venue, year, CCF level) | #1 |
| #3 | LLM comprehensive analysis → JSON | #1, #2 |
| #4 | Report generation (Markdown + HTML zh/en) | #3 |

### Step Details

**Task 1 — PDF Extraction:**

```bash
# First ensure dependencies are installed
python3 <skill_path>/scripts/check_deps.py

# Then run extraction
python3 <skill_path>/scripts/paper_audit_script.py --step1 <pdf_path> [output_dir]
```

**Task 2 — Reference Investigation:**
For each method/issue found, search for its original paper and verify:
- Venue (conference/journal)
- CCF level (A/B/C)
- Year (是否为近3年: 2023-2026)

**Task 3 — LLM Analysis (JSON output):**
Analyze paper and produce structured JSON with:
- Basic info (title, author, institution)
- Main problems (≤3, each linked to innovations)
- Innovations (≤3, each linked to problems and evaluations)
- Evaluation (datasets, metrics, results, limitations)
- Method vs Baseline comparison
- Incremental improvement identification

**Task 4 — Report Generation (Agent):**
Generate 3 files from JSON:
1. `paper_audit_report_YYYYMMDD_HHMMSS.md` — Chinese Markdown
2. `paper_audit_report_YYYYMMDD_HHMMSS_zh.html` — Chinese HTML
3. `paper_audit_report_YYYYMMDD_HHMMSS_en.html` — English HTML

## Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'pdfplumber'` | Run `python3 -m pip install pdfplumber pymupdf pypdf` |
| `ModuleNotFoundError: name 'Dict' is not defined` | The script already includes `from typing import Dict, List, Optional, Any` |
| PDF is scanned/image-based | Use OCR tool first, then feed text to the script |

## CCF Reference

**CCF-A Conferences:** NeurIPS, ICML, ICLR, ACL, EMNLP, AAAI, IJCAI, ASE, ICSE, FSE, ISSTA, OOPSLA, PLDI, POPL, SIGIR, KDD, WWW, CHI
**CCF-A Journals:** IEEE TPAMI, IJCV, JMLR, ACM Computing Surveys, IEEE TNNLS, IEEE TKDE, IEEE TSE

## Constraints

| Type | Max | If Exceeded |
|------|-----|-------------|
| Evaluation metrics | 3 | Merge related metrics |
| Problems | 3 | Merge root-cause related |
| Innovations | 3 | Merge method-similar |
| Contributions | 3 | Refine to core contributions |

## Dependencies

```bash
python3 -m pip install pymupdf pdfplumber pypdf
```

## References

- CCF list: `references/CCF-List.md`
