# BUAA Thesis Audit

北航硕士论文格式自动化检测工具，用于验证论文是否符合《北京航空航天大学学位论文书写规范与排版格式》。

## Installation / 安装

Install using the `skills` CLI:

```bash
# Install globally (recommended)
npx skills add yylonly/buaa-thesis-checker/buaa-thesis-format-checking --global

# Or install locally in current project
npx skills add yylonly/buaa-thesis-checker/buaa-thesis-format-checking
```

For more commands, see `npx skills --help`.

## 功能特性

| 检测项 | 类型 | 说明 |
|--------|------|------|
| 空白页面 | ⚠️ 警告 | 检测无内容页面 |
| 占位符 | ⚠️ 警告 | XXX, \*\*\*\*, TODO, TBD 等 |
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
pip install pypdf
# 字体检测和详细间距分析（推荐）
pip install pymupdf
# PDF 报告生成（可选）
pip install weasyprint        # 推荐，中文支持最好
# 或
pip install reportlab        # 备选
```

macOS Homebrew Python 可能需要额外标志：

```bash
pip install --break-system-packages weasyprint
```

## 快速开始

```bash
python3 scripts/thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]
```

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `pdf_path` | ✅ | 论文 PDF 文件路径 |
| `output_dir` | ❌ | 报告输出目录（默认当前目录） |
| `--type` / `-t` | ❌ | `cn` 中文论文，`en` 英文论文 |

**示例：**

```bash
# 中文论文
python3 scripts/thesis_audit_script.py thesis.pdf --type cn

# 英文论文
python3 scripts/thesis_audit_script.py thesis.pdf -t en

# 指定输出目录
python3 scripts/thesis_audit_script.py thesis.pdf ./output --type cn
```

## 输出报告

检测完成后生成双语报告（Markdown + PDF）：

- **执行摘要** — 问题与警告统计
- **问题项列表** — 需要修复的严重问题
- **警告项列表** — 建议检查的事项
- **检测规范参考** — 相关格式要求说明
- **页码索引** — 问题出现的具体位置

报告命名：`{论文名}_audit_report_{时间戳}.md/.pdf`

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

### URL 位置规范

正文中的 URL 应移至脚注，不应直接出现在正文中（参考文献部分除外）。

### arXiv 引用规范

参考文献中的 arXiv preprint 应已有正式出版物 DOI。

## 脚本结构

```
scripts/
├── thesis_audit_script.py   # 主入口，编排各模块
├── extractors/
│   └── content.py          # PDF 内容提取（ContentExtractor 类）
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
│   ├── fonts.py            # 字体检测（使用PyMuPDF，显示问题文字）
│   └── font_line_spacing.py # 字体与行间距检测
└── reports/
    └── generator.py         # HTML报告生成
```

## 添加新检测项

如需添加新检测项，在 `scripts/checks/` 下创建独立模块：

```python
# scripts/checks/my_check.py
from typing import List, Dict

def check_my_item(content_by_page: List[Dict], ...) -> Dict:
    """
    检测说明

    Returns:
        Dict with keys: ..., warnings: List[str]
    """
    warnings = []

    # 检测逻辑...

    if found_something:
        warnings.append("发现 xxx 问题")

    return {
        'my_result_key': ...,
        'warnings': warnings
    }
```

然后在 `scripts/checks/__init__.py` 中导出，在 `thesis_audit_script.py` 的 `run_full_audit()` 中调用即可。

## 检测报告示例

```
============================================================
论文格式检测报告 / Thesis Format Audit Report
============================================================

PDF 路径: xxx.pdf
总页数: xxx
平均每页字符数: xxx

============================================================
❌ 问题项 / Issues Found:
============================================================
  • [具体问题]

============================================================
⚠️  警告项 / Warnings:
============================================================
  • [具体警告]

============================================================
✅ 通过项:
============================================================
  • [通过的检测项]

检测完成
============================================================
```

## 注意事项

1. **PDF 限制**：PDF 文本提取可能无法获取精确字体信息，建议结合 Word 模板校验
2. **图像页**：纯图表页内容较少属正常现象
3. **封面占位符**：隐私保护用的 `****` 占位符属正常

## 相关文档

- [第三章：书写规范与排版格式](./references/Chapter-3-Writing-Standard-and-Printing-Styles.md)
