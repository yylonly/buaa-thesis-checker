---
name: cn-to-en-translator
description: 中文Word文档(.doc/.docx)翻译为地道英文文档。用于课程大纲、学术论文、报告等中英文翻译工作流。触发：用户提到"翻译成英文"、"中翻英"、"translate to English"，或涉及.doc/.docx文件需要中译英。功能：文件格式转换、专业翻译、地道表达验证、生成英文Word文档。
compatibility: Requires textutil (macOS) or python-docx for file handling; minimax-docx for output generation.
metadata:
  author: yylonly
  version: "1.0"
allowed-tools: Bash python Read Write WebSearch
---

# Chinese to English Document Translator

## When to Use

Activate when user mentions: "翻译成英文"、"中翻英"、"translate to English", or provides .doc/.docx files needing Chinese-to-English translation.

## Workflow

### Step 1: Extract Document Text

**For .doc files:**
```bash
textutil -convert txt -stdout "input.doc" 2>/dev/null
```

**For .docx files:**
```bash
unzip -p input.docx word/document.xml | sed 's/<[^>]*>//g' | tr -s ' \n'
```

### Step 2: Translate

Principles:
- Maintain professional/academic tone
- Preserve structure (headings, sections, tables)
- Use appropriate English terminology
- Mark uncertain expressions with `[CHECK: original Chinese]`

### Step 3: Verify Idiomatic Expressions

For marked `[CHECK:]` expressions:
```bash
brave search "<expression>" academic
```

### Step 4: Create Output Document

Use minimax-docx to generate `.docx`:
```bash
dotnet run --project <skill_path>/../minimax-docx/scripts/dotnet/MiniMaxAIDocx.Cli -- create \
  --type academic \
  --title "Document Title" \
  --output /path/to/output.docx
```

## Common Mappings

| Chinese | English |
|---------|---------|
| 专业基础课 | core professional course |
| 培养目标 | educational objectives |
| 教学目标 | course objectives |
| 学时 | contact hours |
| 毕业要求 | graduation requirements |
| 考核方式 | assessment methods |
| 实验课 | laboratory sessions |
| 课程教学大纲 | course syllabus |
| 黑盒测试/白盒测试 | black-box testing / white-box testing |

## Verification Checklist

- [ ] All `[CHECK:]` expressions addressed
- [ ] Table structures match source
- [ ] Section numbering consistent
- [ ] Professional terminology consistent
- [ ] Output is valid `.docx` format

## Output

Always output as `.docx` (modern Word format). If user requests `.doc`, explain the difference and provide `.docx` instead.
