---
name: buaa-thesis-format-checking
description: |
  北航硕士论文格式检测工具。用于自动化检测北京航空航天大学硕士论文的格式规范性。
  触发场景：用户提到"检测论文"、"格式检查"、" thesis audit"、"论文规范"、或需要运行格式检测脚本时。
  Also triggers when user mentions checking thesis format compliance, verifying BUAA thesis standards, or auditing master's thesis for compliance issues.
  功能：检测空白页面、占位符、章节连续性、过渡段（2-3级标题之间）、URL位置（应在脚注）、arXiv引用是否有DOI、中英文摘要检查、文本对齐方式（justify两端对齐）检测等。
---

# BUAA Thesis Audit Skill

北航硕士论文格式自动化检测工具，用于验证论文是否符合《北京航空航天大学学位论文书写规范与排版格式》。

## 检测功能

本skill执行以下检测项：

| 检测项 | 类型 | 说明 |
|--------|------|------|
| 空白页面 | ⚠️ 警告 | 检测无内容页面 |
| 占位符 | ⚠️ 警告 | XXX, ****, TODO, TBD等 |
| 章节连续性 | ✅/❌ | Chapter 1-5是否完整 |
| 低内容页面 | ⚠️ 警告 | 内容<20%平均值的页面 |
| 未完成标记 | ⚠️ 警告 | "to be continued"等 |
| 过渡段 | ⚠️ 警告 | 二级与三级标题之间 |
| URL位置 | ❌ 问题 | 正文中的URL应在脚注 |
| arXiv无DOI | ⚠️ 警告 | arXiv引用应已有正式出版 |
| 中英文摘要 | ⚠️ 警告 | 摘要存在性及字数检查 |
| 文本对齐 | ⚠️ 警告 | 正文应使用两端对齐(justify) |
| **字体检测** | ⚠️ 警告 | 正文字体规范(SimSun/Times New Roman)，显示问题文字和当前字体 |
| **字号检测** | ⚠️ 警告 | 正文字号规范(9-10.5pt)，显示问题文字和当前字号 |
| **行间距检测** | ⚠️ 警告 | 中文论文正文应为1.5倍行距 |
| **论文题目字数** | ⚠️ 警告 | 题目应≤25个汉字(符)，超出给出警告 |
| **摘要字数** | ⚠️ 警告 | 博士800-1200字，硕士约500字 |
| **关键词数量** | ⚠️ 警告 | 关键词应为3-5个 |
| **页边距** | ⚠️ 警告 | A4纸，上下左右边距2.5cm，装订线0cm |
| **页码格式** | ⚠️ 警告 | 摘要页用大写罗马数字，正文页用阿拉伯数字 |
| **书脊检测** | ⚠️ 警告 | 总页数≥100页时应制作书脊 |
| **图表清单** | ⚠️ 警告 | 图表较多时应单独列出清单 |
| **章节标题格式** | ⚠️ 警告 | 各章标题格式：中文黑体三号居中，英文Times New Roman |

## 使用方法

### 快速开始

当用户提供PDF文件路径时，执行：

```bash
python3 <skill_path>/scripts/thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]
```

**参数说明:**
- `pdf_path`: 必填，论文PDF文件路径
- `output_dir`: 可选，报告输出目录（默认当前目录）
- `--type` 或 `-t`: 可选，论文类型
  - `cn` - 中文论文（国内学生，使用黑体/宋体规范）
  - `en` - 英文论文（国际学生，使用Times New Roman规范）

**示例:**
```bash
python3 thesis_audit_script.py /path/to/thesis.pdf
python3 thesis_audit_script.py /path/to/thesis.pdf /output/directory
python3 thesis_audit_script.py thesis.pdf --type cn
python3 thesis_audit_script.py thesis.pdf -t en
```

### 依赖要求

仅需 `pypdf`：

```bash
pip install pypdf
```

### 自动化检测流程

1. **提取论文内容** - 使用pypdf读取PDF所有页面
2. **执行各项检测** - 并行运行多个检查函数
3. **生成报告** - 输出中英双语检测报告（Markdown + PDF）

### 输出报告

检测完成后自动生成 HTML 报告：

**报告内容:**
- 问题项列表（包含所有检测问题）
- 下方空白页面

**报告命名:** `{论文名}_audit_report_{时间戳}.html`

### 脚本结构

脚本采用模块化设计，结构如下：

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

**主入口**（执行时使用）:
```bash
python3 scripts/thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]
```

## 检测规范参考

### 论文结构要求

根据《北京航空航天大学研究生学位论文撰写规范》（2025年9月）：

| 部分 | 要求 |
|------|------|
| 封面 | 中英文封面、分类号、论文编号、密级（保密论文） |
| 题名页 | 封面内容更详细，含申请学位类别、学科方向等 |
| 独创性声明 | 授权书紧跟独创性声明 |
| 摘要 | 中文博士800-1200字，硕士约500字，关键词3-5个 |
| 目录 | 列至二级节标题（如2.2.1） |
| 正文 | Chapter 1-5，结论 |
| 参考文献 | 格式规范（见第三章） |
| 附录 | 按字母A、B、C编序号 |
| 致谢 | 限一页 |
| 作者简介 | 仅博士需要 |

### 封面格式规范（根据官方模板）

**中文封面**:
- 中图分类号：黑体五号加粗，数字/Times New Roman五号加粗
- 论文编号：10006 + 学号，如10006SY0104106
- 密级：黑体五号加粗，保密论文需标注保密期限
- 论文题目：**≤25个汉字（符）**，超长需精简
- 作者信息：黑体四号，左对齐，首行缩进8字符

**页边距**: 上-2.5cm，下-2.5cm，左-2.5cm，右-2.5cm，装订线0cm

### 过渡段检测逻辑

**问题**: 二级标题(如1.1)后直接跟三级标题(如1.1.1)，缺少过渡段

**正确格式**:
```
1.1 Section Title (二级标题)
[过渡段 - 至少60字符的衔接内容]
1.1.1 Subsection Title (三级标题)
```

**检测规则**:
- 排除目录页（包含"Table of Contents"、罗马数字页码、"........"引导线等）
- 三级标题前累计≥60字符的非标题内容视为有过渡段

### URL位置规范

**问题**: URL直接出现在正文中
**正确**: URL应在脚注中，或在参考文献中

**检测规则**:
- 排除参考文献页（论文后30页）
- 检测正文中以`https://`或`http://`开头的URL

### arXiv引用规范

**问题**: 参考文献中包含arXiv preprint无DOI
**正确**: arXiv引用应有正式出版物DOI

**检测规则**:
- 仅检测参考文献页
- 识别"arXiv:"或"arxiv:"模式
- 检查是否有"DOI:"同在

### 论文题目字数规范

**问题**: 论文题目超过25个汉字（符）
**正确**: 题目应≤25个汉字（符）

**检测规则**:
- 提取封面中的论文题目
- 统计中文字符数（汉字+中文标点）
- 超25字符给出警告

### 摘要字数规范

**问题**: 摘要字数不符合要求
**正确**: 博士800-1200字，硕士约500字

**检测规则**:
- 提取中文摘要内容
- 统计字符数（不含关键词）
- 超出范围给出警告

### 页码格式规范

**问题**: 页码格式不正确
**正确**: 摘要页用大写罗马数字(ⅠⅡⅢ)，正文页用阿拉伯数字

**检测规则**:
- 识别摘要页（从"摘要"到"主要符号表"部分）
- 检查这些页面是否使用罗马数字格式
- 正文首页应为阿拉伯数字"1"

### 书脊检测

**问题**: 页数≥100页但无书脊
**正确**: 总页数≥100页应制作书脊

**检测规则**:
- 统计论文总页数
- ≥100页检测是否有"书脊"相关内容页

## 输出格式

检测完成后，输出以下格式的报告：

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

## 添加新检测项

如需添加新检测项，推荐在 `scripts/checks/` 下创建独立模块，遵循以下约定：

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

## 注意事项

1. **PDF限制**: PDF文本提取可能无法获取精确字体信息，建议结合Word模板校验
2. **图像页**: 纯图表页内容较少属正常现象
3. **封面占位符**: 隐私保护用的****占位符属正常

## 参考文档

- 规范文档: `references/Chapter-3-Writing-Standard-and-Printing-Styles.md`
- 官方撰写规范（2025年9月）: `references/附件1：北京航空航天大学研究生学位论文撰写规范.pdf`
- 样式模板: `references/附录A：学位论文部分样式模板.pdf`
- 样例论文（Word版）: `references/附件2：学位论文样例（word）版.pdf`
