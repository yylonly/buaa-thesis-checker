---
name: buaa-thesis-format-checking
description: |
  北航硕士论文格式检测工具。用于自动化检测北京航空航天大学硕士论文的格式规范性。
  触发场景：用户提到"检测论文"、"格式检查"、" thesis audit"、"论文规范"、或需要运行格式检测脚本时。
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
| 字体检测 | ⚠️ 警告 | 正文字体规范(SimSun/Times New Roman) |
| 字号检测 | ⚠️ 警告 | 正文字号规范(9-10.5pt) |
| 行间距检测 | ⚠️ 警告 | 中文论文正文应为1.5倍行距 |

## 工作流程

本skill采用**Task工具**分步执行，最后进行报告审核验证：

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: PDF文本提取 (脚本)                                      │
│  使用 pypdf 提取论文内容，保存到 thesis_text_extracted.json       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Agent执行格式检测                                       │
│  读取临时文件，并行执行14项检测                                  │
│  保存到 thesis_check_results.json                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Agent生成JSON报告 (脚本)                               │
│  读取检测结果，生成JSON格式报告用于审核                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Agent审核报告准确性                                    │
│  核实检测结果是否准确，如有问题返回Step 2重新检测                │
│  一致后继续Step 5                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌───────────────────┐
                    │  审核通过?        │
                    └───────────────────┘
                      ↓ 是              ↓ 否
              ┌─────────────┐    ┌─────────────┐
              │ Step 5:     │    │ 返回Step 2  │
              │ 生成HTML报告 │    │ 重新检测    │
              └─────────────┘    └─────────────┘
```

## 使用方法

### 快速开始

当用户提供PDF文件路径时，执行：

```bash
python3 <skill_path>/scripts/thesis_audit_script.py <pdf_path> [output_dir] [--type cn|en]
```

### Task执行步骤

#### Step 1: PDF文本提取（脚本直接执行）

```bash
python3 <skill_path>/scripts/thesis_audit_script.py --step1 <pdf_path> [output_dir]
```

---

#### Step 2: Agent执行格式检测

**Agent提示词**:
```
请执行以下命令进行14项格式检测：
```bash
python3 <skill_path>/scripts/thesis_audit_script.py --step2 <text_path> --type cn
```
```

**输出**: `thesis_check_results.json`

---

#### Step 3: Agent生成JSON报告

**Agent提示词**:
```
请执行以下命令生成JSON报告：
```bash
python3 <skill_path>/scripts/thesis_audit_script.py --step3-json <results_path> <pdf_path>
```
```

**输出**: `{论文名}_audit_report_{时间戳}.json`

---

#### Step 4: Agent审核报告准确性

**Agent提示词**:
```
请审核刚刚生成的JSON检测报告的准确性。

## 审核步骤

1. 读取JSON报告: `{json_report_path}`
2. 读取原始PDF: `{pdf_path}`

## 核实以下关键项

a. **空白页面**: 报告说无空白页，是否正确？
b. **占位符**: 报告说无占位符，是否正确？
c. **章节连续性**: 5章是否完整？
d. **低内容页面**:
   - 第1页是封面，内容少正常
   - 第74页是"攻读硕士学位期间取得的研究成果 - 无"，这是标准格式页面，不是问题
e. **未完成标记**: 无"to be continued"等标记
f. **正文对齐**: 表格页左对齐正常；正文大部分两端对齐
g. **行距**: 核实实际行距

## 常见误报规避

- "攻读硕士学位期间取得的研究成果 - 无" - 这是正确格式
- 表格页的左对齐 - 表格格式本就如此
- 封面页内容少 - 封面本身就信息量少

## 输出审核结果

如果报告准确：
```
## 审核结论
✅ 审核通过
JSON报告: {json_report_path}
```

如果需要修正：
```
## 审核结论
⚠️ 需要修正
问题项: 1. xxx 2. xxx
建议: 返回Step 2重新检测
```
```

---

#### Step 5: 生成HTML报告（审核通过后）

**Agent提示词**:
```
审核已通过，请执行以下命令生成HTML报告：
```bash
python3 <skill_path>/scripts/thesis_audit_script.py --step3-html <results_path> <pdf_path>
```
```

**输出**: `{论文名}_audit_report_{时间戳}.html`

---

## 完整执行流程

```
1. TaskCreate - 创建任务
2. Step 1 (脚本) - 提取PDF文本
3. Step 2 (Agent) - 执行14项检测
4. Step 3 (脚本) - 生成JSON报告
5. Step 4 (Agent) - 审核报告准确性
   ↓ 审核通过
6. Step 5 (脚本) - 生成HTML报告
   ↓ 审核不通过
   返回 Step 2 重新检测
```

---

## 脚本命令参考

```bash
# Step 1: 提取PDF文本
python3 thesis_audit_script.py --step1 thesis.pdf /output/dir

# Step 2: 执行格式检测
python3 thesis_audit_script.py --step2 thesis_text_extracted.json --type cn

# Step 3: 生成JSON报告（用于审核）
python3 thesis_audit_script.py --step3-json thesis_check_results.json thesis.pdf

# Step 4: 审核（由Agent执行）
# ...

# Step 5: 生成HTML报告（审核通过后）
python3 thesis_audit_script.py --step3-html thesis_check_results.json thesis.pdf
```

---

## 脚本结构

```
scripts/
├── thesis_audit_script.py   # 主入口，支持 --step1/2/3-json/3-html
├── extractors/
│   └── content.py          # PDF 内容提取
├── checks/                 # 各检测项模块
│   ├── blank_pages.py
│   ├── placeholders.py
│   ├── section_continuity.py
│   ├── low_content_pages.py
│   ├── incomplete_content.py
│   ├── transition_paragraphs.py
│   ├── urls_in_body.py
│   ├── arxiv_without_doi.py
│   ├── abstracts.py
│   ├── text_alignment.py
│   ├── figure_pages.py
│   ├── fonts.py
│   └── font_line_spacing.py
└── reports/
    └── generator.py         # JSON和HTML报告生成
```

---

## 依赖要求

```bash
pip install pypdf pymupdf
```

---

## 注意事项

1. **PDF限制**: PDF文本提取可能无法获取精确字体信息
2. **标准格式页面**: "攻读硕士学位期间取得的研究成果 - 无"是正确格式
3. **表格页对齐**: 表格左对齐是正常格式，不是问题

---

## 参考文档

- 规范文档: `references/Chapter-3-Writing-Standard-and-Printing-Styles.md`
- 官方撰写规范: `references/附件1：北京航空航天大学研究生学位论文撰写规范.pdf`
