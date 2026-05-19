# BUAA Thesis Checker

面向北京航空航天大学学位论文评审场景的 Agent Skills 集合，提供论文格式检查、论文内容审核、综合评审意见生成，以及中文 Word 文档英译能力。

本仓库不是一个单一命令行应用，而是一组可安装到 Agent/Codex/Claude Code 工作流中的技能包。每个技能目录都包含 `SKILL.md`、可复用脚本和必要参考资料。

## 功能概览

| Skill | 用途 | 主要输出 |
| --- | --- | --- |
| `buaa-thesis-format-checking` | 北航论文格式自动化检查 | JSON/HTML 格式检查报告 |
| `buaa-thesis-content-checking` | 学术内容审核，分析贡献、创新、实验与 baseline | Markdown/HTML 内容审核报告 |
| `buaa-thesis-checking` | 串联格式检查和内容审核，生成正式评审意见 | 综合 Markdown/HTML 评审意见 |
| `cn-to-en-translator` | 中文 `.doc/.docx` 文档翻译为英文 Word 文档 | 英文 `.docx` |

## 仓库结构

```text
buaa-thesis-checker/
├── README.md
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
├── plugins/
│   └── buaa-thesis-checker/
│       ├── .codex-plugin/plugin.json
│       ├── .claude-plugin/plugin.json
│       ├── README.md
│       └── skills/
├── buaa-thesis-checking/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── buaa-thesis-format-checking/
│   ├── SKILL.md
│   ├── README.md
│   ├── references/
│   └── scripts/
│       ├── thesis_audit_script.py
│       ├── checks/
│       ├── extractors/
│       └── reports/
├── buaa-thesis-content-checking/
│   ├── SKILL.md
│   ├── README.md
│   ├── evals/
│   ├── references/
│   └── scripts/
│       ├── check_deps.py
│       ├── paper_audit_script.py
│       ├── checks/
│       ├── extractors/
│       └── reports/
└── cn-to-en-translator/
    ├── SKILL.md
    └── scripts/
```

## 安装

本仓库同时提供三种集成方式：

1. 直接安装单个 Agent Skill
2. 通过 Codex plugin marketplace 安装
3. 通过 Claude Code plugin marketplace 或 `--plugin-dir` 加载

### Agent Skills

使用 `skills` CLI 从 GitHub 安装单个或全部技能：

```bash
# 查看仓库内可安装的技能
npx skills add yylonly/buaa-thesis-checker --list

# 安装所有技能到全局
npx skills add yylonly/buaa-thesis-checker --all --global

# 只安装格式检查技能
npx skills add yylonly/buaa-thesis-checker --skill "buaa-thesis-format-checking"

# 更新已安装技能
npx skills update
```

也可以直接在仓库内运行各技能的 Python 脚本，适合调试或批处理。

### Codex Plugin

Codex 插件位于：

```text
plugins/buaa-thesis-checker/
```

插件 manifest：

```text
plugins/buaa-thesis-checker/.codex-plugin/plugin.json
```

仓库内 Codex marketplace：

```text
.agents/plugins/marketplace.json
```

该 marketplace 指向本仓库的本地插件路径 `./plugins/buaa-thesis-checker`，便于在 Codex 插件 UI 或本地 marketplace 流程中发现和安装。

### Claude Code Plugin

Claude Code 插件使用同一个插件目录，并额外提供 Claude Code manifest：

```text
plugins/buaa-thesis-checker/.claude-plugin/plugin.json
```

本地开发测试：

```bash
claude --plugin-dir ./plugins/buaa-thesis-checker
```

通过本仓库的 Claude Code marketplace 安装：

```bash
claude plugin marketplace add .
claude plugin install buaa-thesis-checker@buaa-thesis-tools
```

Claude Code marketplace 文件：

```text
.claude-plugin/marketplace.json
```

安装后技能会被命名空间化，例如：

```text
/buaa-thesis-checker:buaa-thesis-checking
/buaa-thesis-checker:buaa-thesis-format-checking
/buaa-thesis-checker:buaa-thesis-content-checking
/buaa-thesis-checker:cn-to-en-translator
```

## 依赖

建议使用 Python 3.10+。

格式检查：

```bash
python3 -m pip install pdfminer.six pymupdf pypdf
```

内容审核：

```bash
python3 -m pip install pymupdf pdfplumber pypdf
```

内容审核如果需要 API 驱动的自动 LLM 提取，可额外安装：

```bash
python3 -m pip install anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

内容审核目录提供依赖检查脚本：

```bash
python3 buaa-thesis-content-checking/scripts/check_deps.py --check-only
python3 buaa-thesis-content-checking/scripts/check_deps.py --yes
```

## 快速使用

### 1. 综合评审

推荐通过 Agent 技能调用：

```text
Use $buaa-thesis-checking to review this BUAA thesis PDF and write the two required academic comments.
```

该技能会先执行格式检查，再核对可能误报，然后执行内容审核，最后生成两个核心评审块：

- 学术评语
- 不足、问题与修改意见

输出包括机器可读的 Markdown 和自包含 HTML 报告。

### 2. 格式检查

完整流程：

```bash
python3 buaa-thesis-format-checking/scripts/thesis_audit_script.py thesis.pdf ./output --type cn
```

分步执行，便于复核中间产物：

```bash
python3 buaa-thesis-format-checking/scripts/thesis_audit_script.py --step1 thesis.pdf ./output
python3 buaa-thesis-format-checking/scripts/thesis_audit_script.py --step2 ./output/thesis_text_extracted.json --type cn
python3 buaa-thesis-format-checking/scripts/thesis_audit_script.py --step3-json ./output/thesis_check_results.json thesis.pdf ./output
python3 buaa-thesis-format-checking/scripts/thesis_audit_script.py --step3-html ./output/thesis_check_results.json thesis.pdf ./output
```

`--type` 可选值：

- `cn`：中文论文，默认值
- `en`：英文论文

检测项包括空白页、占位符、章节连续性、低内容页、未完成标记、过渡段、正文 URL、arXiv 无 DOI、中英文摘要、文本对齐、图表页统计、字体字号、行间距和详细间距。

注意：格式检查结果应视为候选问题。封面、声明页、目录页、表格页、图表页等容易产生低内容或对齐类误报，正式评审前需要人工或 Agent 复核。

### 3. 内容审核

先检查依赖：

```bash
python3 buaa-thesis-content-checking/scripts/check_deps.py --check-only
```

审核 PDF：

```bash
python3 buaa-thesis-content-checking/scripts/paper_audit_script.py thesis.pdf ./output
```

也可以直接审核文本：

```bash
python3 buaa-thesis-content-checking/scripts/paper_audit_script.py --text "论文全文内容..." ./output
```

内容审核关注：

- 主要贡献是否清晰且不超过 3 个核心点
- 方法创新是否能追溯到研究问题
- 实验设计、数据集、指标、baseline 和消融是否支撑结论
- 是否存在只做增量改进但表述为强创新的问题
- 是否能形成 `问题 -> 方法/创新 -> 实验证据` 的链条

### 4. 中文文档英译

通过 `cn-to-en-translator` 技能处理 `.doc` 或 `.docx` 文件。技能会提取原文、保留结构、翻译为专业英文，并生成现代 Word `.docx` 输出。

触发示例：

```text
Use $cn-to-en-translator to translate this Chinese syllabus into English.
```

## 输出文件

不同技能会生成不同命名的报告文件：

| 技能 | 常见文件 |
| --- | --- |
| 格式检查 | `thesis_text_extracted.json`, `thesis_check_results.json`, `*_audit_report_*.json`, `*_audit_report_*.html` |
| 内容审核 | `paper_audit_report_*.md`, `paper_audit_report_*_zh.html`, `paper_audit_report_*_en.html` |
| 综合评审 | `buaa_thesis_review_*.md`, `buaa_thesis_review_*.html` |
| 中英翻译 | 英文 `.docx` 文件 |

建议每篇论文使用独立输出目录，避免并行或重复运行时中间文件相互覆盖。

## 设计原则

- 自动检查只提供候选结论，正式评语必须基于证据复核。
- 综合评审优先生成可用于学位论文评阅的正式中文意见，而不是长清单。
- 内容审核限制核心问题、贡献和创新数量，避免把枝节改动包装成主要贡献。
- HTML 报告应自包含、可离线打开，适合给人阅读；Markdown 报告适合后续编辑和机器处理。

## 维护说明

每个技能遵循 Agent Skills 结构：

- `SKILL.md`：技能元数据、触发条件、工作流和注意事项
- `scripts/`：可复用脚本
- `references/`：规范、模板或参考资料
- `README.md`：技能级说明文档，若存在

修改技能行为时，优先同步更新对应目录下的 `SKILL.md` 和根目录 `README.md`。

## License

MIT License
