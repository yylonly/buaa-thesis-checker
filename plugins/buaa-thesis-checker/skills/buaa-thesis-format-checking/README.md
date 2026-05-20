# BUAA Thesis Audit

北航硕士论文格式自动化检测工具，用于验证论文是否符合《北京航空航天大学学位论文书写规范与排版格式》。

## 功能特性

| 检测项 | 类型 | 说明 |
|--------|------|------|
| 空白页面 | ⚠️ 警告 | 检测无内容页面 |
| 占位符 | ⚠️ 警告 | XXX, ****, TODO, TBD 等 |
| 章节连续性 | ✅/❌ | Chapter 1-5 是否完整 |
| 低内容页面 | ⚠️ 警告 | 内容 < 20% 平均值的页面 |
| 未完成标记 | ⚠️ 警告 | "to be continued" 等 |
| 过渡段 | ⚠️ 警告 | 二级与三级标题之间缺少衔接 |
| URL 位置 | ❌ 问题 | 正文中的 URL 应在脚注 |
| arXiv 无 DOI | ⚠️ 警告 | arXiv 引用应已有正式出版 |
| 中英文摘要 | ⚠️ 警告 | 摘要存在性及字数检查 |
| 文本对齐 | ⚠️ 警告 | 正文应使用两端对齐 (justify) |
| 字体检测 | ⚠️ 警告 | 正文字体规范(SimSun/Times New Roman)，显示问题文字和当前字体 |
| 字号检测 | ⚠️ 警告 | 正文字号规范(9-10.5pt)，显示问题文字和当前字号 |
| 行间距检测 | ⚠️ 警告 | 中文论文正文应为1.5倍行距 |

## 安装依赖

```bash
# 核心依赖 - PDF文本提取（使用 PDFMiner.six，精度更高）
pip install pdfminer.six

# 字体检测和详细间距分析（推荐）
pip install pymupdf
```

## 快速开始

```bash
# 完整流程（Step 1-5）
python3 scripts/thesis_audit_script.py <pdf_path> [output_dir] --type cn|en

# 分步执行
python3 scripts/thesis_audit_script.py --step1 <pdf_path> [output_dir]   # 提取PDF文本
python3 scripts/thesis_audit_script.py --step2 <text_path> --type cn|en   # 执行格式检测
python3 scripts/thesis_audit_script.py --step3-json <results_path> <pdf>  # 生成JSON报告
python3 scripts/thesis_audit_script.py --step3-html <results_path> <pdf>  # 生成HTML报告
```

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `pdf_path` | ✅ | 论文 PDF 文件路径 |
| `output_dir` | ❌ | 报告输出目录（默认当前目录） |
| `--type` / `-t` | ❌ | `cn` 中文论文，`en` 英文论文 |

## 5步检测流程

本工具采用 5 步检测流程，Step 2 和 Step 4 可使用 Agent 并行执行：

```
┌─────────────────────────────────────────────────────┐
│  Step 1: PDF 文本提取（脚本直接执行）                 │
│  使用 PDFMiner.six 提取论文内容                      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  Step 2: Agent 执行 14 项格式检测                    │
│  并行执行各项检测，保存到 thesis_check_results.json   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  Step 3: Agent 生成 JSON 报告（脚本）                │
│  读取检测结果，生成 JSON 格式报告用于审核             │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  Step 4: Agent 审核报告准确性                        │
│  核实检测结果是否准确，如有问题返回 Step 2 重新检测   │
└─────────────────────────────────────────────────────┘
                          ↓
                    ┌─────────────┐
                    │  审核通过?  │
                    └─────────────┘
                      ↓ 是              ↓ 否
              ┌─────────────┐    ┌─────────────┐
              │  Step 5:   │    │  返回Step 2 │
              │  生成HTML报告│    │  重新检测   │
              └─────────────┘    └─────────────┘
```

## 输出报告

检测完成后生成：

- **JSON 报告** — 机器可读的检测结果，用于审核验证
- **HTML 报告** — 人类可读的完整检测报告

报告命名：`{论文名}_audit_report_{时间戳}.json/.html`

## 规范参考

### 论文结构要求

| 部分 | 要求 |
|------|------|
| 封面 | 中英文封面、分类号、论文编号 |
| 摘要 | 中文约 500 字，关键词 3-5 个 |
| 目录 | 三级标题结构 |
| 正文 | Chapter 1-5 |
| 参考文献 | 格式规范 |
| 致谢 | 限一页 |

### 过渡段规范

二级标题（如 1.1）后直接跟三级标题（如 1.1.1）视为不规范，需有过渡段：

```
1.1 Section Title
[至少 60 字符的过渡段]
1.1.1 Subsection Title
```

### 误报规避

以下为标准格式，不是问题：

- "攻读硕士学位期间取得的研究成果 - 无" — 标准格式页
- 表格页的左对齐 — 表格格式本就如此
- 封面页内容少 — 封面本身就信息量少
- PDF文本提取导致行长度变化大 — 字体/对齐检测需结合 PyMuPDF 视觉分析

## 脚本结构

```
scripts/
├── thesis_audit_script.py   # 主入口，编排各模块
├── extractors/
│   └── content.py          # PDF 内容提取（PDFMiner.six）
├── checks/                 # 各检测项独立模块
│   ├── blank_pages.py      # 空白页面检测
│   ├── placeholders.py     # 占位符检测
│   ├── section_continuity.py # 章节连续性检测
│   ├── low_content_pages.py  # 低内容页面检测（含下方空白检测）
│   ├── incomplete_content.py # 未完成标记检测
│   ├── transition_paragraphs.py # 过渡段检测
│   ├── urls_in_body.py     # URL 位置检测
│   ├── arxiv_without_doi.py # arXiv DOI 检测
│   ├── abstracts.py         # 中英文摘要检测
│   ├── text_alignment.py    # 文本对齐检测
│   ├── figure_pages.py      # 图表页面统计
│   ├── fonts.py            # 字体检测（PyMuPDF，显示问题文字）
│   └── font_line_spacing.py # 字体与行间距检测
└── reports/
    └── generator.py         # JSON/HTML 报告生成
```

## 注意事项

1. **PDF 文本提取**：使用 PDFMiner.six，精度比 pypdf 更高（平均每页多 2% 字符）
2. **字体检测**：需要安装 PyMuPDF 进行视觉分析
3. **图像页**：纯图表页内容较少属正常现象
4. **封面占位符**：隐私保护用的 `****` 占位符属正常

## 相关文档

- [第三章：书写规范与排版格式](./references/Chapter-3-Writing-Standard-and-Printing-Styles.md)
