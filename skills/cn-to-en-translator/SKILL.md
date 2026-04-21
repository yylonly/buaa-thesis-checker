---
name: cn-to-en-translator
description: Translate Chinese Word documents (.doc/.docx) to idiomatic English. Use this skill whenever the user wants to translate a Chinese document to English, including course syllabi, academic papers, reports, or any bilingual document workflow. The skill handles file conversion, professional translation with idiomatic verification, and outputs a properly formatted English Word document. Trigger whenever you see ".doc" or ".docx" files that need Chinese-to-English translation, or when user says "translate to English", "中翻英", "翻译成英文", or similar requests.
---

# Chinese to English Document Translator

This skill translates Chinese Word documents to natural, idiomatic English. It handles the complete workflow from input file to polished output.

## Workflow

### Step 1: Read the Input Document

**For .doc files** (binary format):
```bash
textutil -convert txt -stdout "input.doc" 2>/dev/null
```

**For .docx files**:
```bash
unzip -p input.docx word/document.xml | sed 's/<[^>]*>//g' | tr -s ' \n'
```
Or use the Read tool directly on the docx.

If both fail, ask the user to provide the text content directly.

### Step 2: Translate to English

Translate the content following these principles:

1. **Maintain professional/academic tone** - This skill is designed for course syllabi, academic documents, and professional reports
2. **Preserve structure** - Keep headings, sections, tables, and formatting hierarchy
3. **Use appropriate terminology** - Software engineering terms should use standard English equivalents
4. **Mark uncertain expressions** - Use `[CHECK: original Chinese]` for expressions you're unsure about whether they're idiomatic

### Step 3: Verify Idiomatic Expressions (Important!)

For any marked `[CHECK:]` expressions, attempt to verify using Brave API:

```bash
brave search "<expression>" academic
```

**Key expressions to verify in academic/technical contexts:**
- "fundamental" vs "basic" concepts (prefer "fundamental" for academic)
- "selection criteria" vs "selection strategies" (prefer "criteria")
- "test case design" vs "test case writing" (prefer "design")
- "fulfill" vs "meet" team member roles (both acceptable)
- "introduction" vs "overview" for chapter titles

If Brave API fails, use your knowledge of academic English conventions and note any uncertainties.

### Step 4: Create the Output Document (uses minimax-docx)

The minimax-docx skill is available at:
`/Users/yylonly/.claude/plugins/cache/minimax-skills/minimax-skills/1.0.0/skills/minimax-docx`

**First, check the environment:**
```bash
bash /Users/yylonly/.claude/plugins/cache/minimax-skills/minimax-skills/1.0.0/skills/minimax-docx/scripts/env_check.sh
```

**If minimax-docx is ready**, use it to create the document:
```bash
cd /Users/yylonly/.claude/plugins/cache/minimax-skills/minimax-skills/1.0.0/skills/minimax-docx
dotnet run --project scripts/dotnet/MiniMaxAIDocx.Cli -- create \
  --type academic \
  --title "Document Title" \
  --output /path/to/output.docx
```

**For complex documents with tables**, create a custom C# script:
```bash
mkdir -p /tmp/docx_build && cd /tmp/docx_build
dotnet new console -n DocCreator -f net10.0
cd DocCreator && dotnet add package DocumentFormat.OpenXml --version 3.2.0
```

Then write the document creation code and run:
```bash
dotnet run
```

### Step 5: Handle Tables

When creating tables in OpenXML:

```csharp
var table = new Table();
table.Append(new TableProperties(new TableBorders(
    new TopBorder { Val = BorderValues.Single, Size = 4 },
    new BottomBorder { Val = BorderValues.Single, Size = 4 },
    // ... more borders
));
// Add rows with TableRow and TableCell
```

## Document Structure to Preserve

Typical Chinese academic documents include:
- Course information header (code, name, credits, etc.)
- Numbered sections (一、二、三 or I, II, III)
- Subsection parts (Part One, Part Two)
- Tables for assessment rubrics
- Lab/project listings

## Output Format

Always output as `.docx` (the modern Word format). If user requests `.doc`, explain the difference and provide `.docx` instead.

## Common Chinese → English Mappings for Academic Documents

| Chinese | English (Preferred) |
|---------|-------------------|
| 专业基础课 | core professional course |
| 培养目标 | educational objectives |
| 教学目标 | course objectives |
| 学时 | contact hours / hours |
| 毕业要求 | graduation requirements |
| 考核方式 | assessment methods |
| 实验课 | laboratory sessions / lab sessions |
| 课程教学大纲 | course syllabus |
| 概要设计 | architectural design |
| 详细设计 | detailed design |
| 软件构造 | software construction |
| 需求工程 | requirements engineering |
| 黑盒测试/白盒测试 | black-box testing / white-box testing |

## Verification Checklist

Before finalizing, ensure:
- [ ] All [CHECK:] expressions have been addressed
- [ ] Table structures match source
- [ ] Section numbering is consistent
- [ ] Professional terminology is used consistently
- [ ] Output file is valid .docx format
