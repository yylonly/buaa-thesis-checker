# BUAA Thesis Checker — Agent Skills

A collection of Claude Code skills for BUAA (Beijing University of Aeronautics and Astronautics) thesis checking and document translation.

## Installation

```bash
# Install a specific skill
npx skills add yylonly/buaa-thesis-checker --skill "buaa-thesis-format-checking"

# Install all skills globally
npx skills add yylonly/buaa-thesis-checker --all --global

# List available skills
npx skills add yylonly/buaa-thesis-checker --list

# Update skills
npx skills update
```

For full commands, see `npx skills --help`.

## Skills

### buaa-thesis-format-checking

北航硕士论文格式自动化检测工具。

**Triggers:** 检测论文、格式检查、thesis audit、论文规范

**Detects:** 空白页面、占位符、章节连续性、过渡段、URL位置、中英文摘要、文本对齐、字体字号、行间距等14项

**Tools:** Bash, python, Read, TaskCreate, TaskUpdate, TaskList

---

### buaa-thesis-content-checking

学术论文内容审核工具。

**Triggers:** 审核论文、论文评审、paper review、论文创新性、论文贡献、论文对比baseline

**Features:** 追溯关系图(P→I→E)、CCF顶会顶刊判断、贡献点约束(≤3个)、Markdown+HTML中英文报告

**Tools:** Bash, python, Read, TaskCreate, TaskUpdate, TaskList, WebSearch, Agent

---

### cn-to-en-translator

中文Word文档(.doc/.docx)翻译为地道英文。

**Triggers:** 翻译成英文、中翻英、translate to English

**Features:** 文件格式转换、专业翻译、地道表达验证、生成英文Word文档

**Tools:** Bash, python, Read, Write, WebSearch

---

## Structure

```
buaa-thesis-checker/
├── buaa-thesis-format-checking/
│   └── SKILL.md
├── buaa-thesis-content-checking/
│   └── SKILL.md
├── cn-to-en-translator/
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
└── README.md
```

## Skill Format

Each skill follows the [Agent Skills spec](https://github.com/vercel-labs/skills):

- `SKILL.md` with YAML frontmatter (name, description, allowed-tools)
- Markdown body with workflow instructions
- Optional `scripts/` and `references/` directories
