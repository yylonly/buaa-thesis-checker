# Agent Skills

A collection of Claude Code skills for various tasks.

## Installation

Install skills using the `skills` CLI:

```bash
# Install a specific skill from GitHub
npx skills add yylonly/buaa-thesis-checker

# Install globally (available to all projects)
npx skills add yylonly/buaa-thesis-checker --global

# List all available skills in this repo
npx skills add yylonly/buaa-thesis-checker --list

# Remove a skill
npx skills remove buaa-thesis-checker

# Check for updates
npx skills check

# Update all skills
npx skills update
```

For more commands, see `npx skills --help`.

## Available Skills

### buaa-thesis-format-checking
北航硕士论文格式检测工具。用于自动化检测北京航空航天大学硕士论文的格式规范性。

**功能:** 空白页面、占位符、章节连续性、过渡段、URL位置、arXiv无DOI、中英文摘要、文本对齐、字体检测、字号检测、行间距、论文题目字数、摘要字数、关键词数量、页边距、页码格式、书脊检测、图表清单、章节标题格式等。

**Trigger:** 用户提到"检测论文"、"格式检查"、"thesis audit"、"论文规范"

### buaa-thesis-content-checking
论文内容审核工具。用于审核学术论文的主要贡献、方法创新性、实验评估，以及与baseline的详细对比。

**功能:** 追溯关系图（问题→创新→验证）、主要问题分析、方法创新性、评估验证（数据集/指标/结果/局限性）、方法vs Baseline详细对比、CCF顶会顶刊判断、贡献点数量约束检查（≤3个）。

**Trigger:** 用户提到"审核论文"、"论文评审"、"paper review"、"论文创新性"、"论文贡献"、"论文对比baseline"
