# Resume Formatter Skill - Implementation Plan

## Executive Summary

This skill enables **robust** conversion of applicant resumes into specific company-required formats. It goes beyond simple copy-paste by intelligently extracting content from diverse resume layouts and mapping them to target company templates while maintaining content quality.

**Key Differentiator**: Handles real-world resume complexity including multi-column layouts, headers/footers, text boxes, tables, mixed languages, and non-standard formats—not just simple chronological resumes.

**Target Accuracy**: 94-96% for standard formats, 85-92% for complex layouts, 70-85% for edge cases.

## Overview

This skill enables conversion of applicant resumes into specific company-required formats. Unlike resume-translator which focuses on language translation, resume-formatter focuses on extracting content from a source resume and mapping it into a target company template while maintaining content quality.

**Robustness Philosophy**: The skill is designed to handle edge cases and unusual formats gracefully, providing partial results with confidence scores rather than failing completely.

## Purpose

**Primary Users:**
- **Headhunters**: Need to reformat candidate resumes to match client company requirements
- **Recruiting Companies**: Have standardized resume formats that all candidates must use
- **Applicants**: Applying to companies with specific resume template requirements (e.g., J&J, Meta Search, etc.)

**Core Functionality:**
- Extract content from applicant's personal resume format
- Map extracted content to company-specific template fields
- Preserve all applicant information while fitting into required structure
- Handle different template structures (tables, sections, field names)
- Maintain professional quality during transformation

## Skill Structure

Following the skill-creator guidelines, this skill will consist of:

```
resume-formatter/
├── SKILL.md (required)
├── references/ (optional)
│   ├── template_field_mapping.md - Common company template field structures
│   ├── content_extraction_guide.md - How to extract different resume sections
│   └── quality_preservation.md - Maintaining content quality during transformation
├── scripts/ (optional)
│   ├── resume_parser.py - Extract structured content from source resume
│   ├── template_mapper.py - Map content to target template
│   └── content_validator.py - Validate completeness after transformation
└── tests/ (for development/testing)
    ├── format_before/ - Example source resumes
    │   └── 이력서_v2025-10-26_sub_v1.0.docx
    └── format_to/ - Example company templates
        ├── 이력서 양식(JnJ)_template.doc
        ├── 메타써치_국문이력서_샘플.docx
        └── [AHR]이준호.doc
```

## Implementation Phases

### Phase 1: Understanding Concrete Examples (Step 1 from skill-creator)

**Real Use Cases from Test Files:**

**Source Resume** (`tests/format_before/이력서_v2025-10-26_sub_v1.0.docx`):
- Applicant: 문다빈 (Dabin Moon)
- Structure: Free-form sections (기술/Skills, 경력/Experience)
- Content: Detailed technical work experience at Hudson AI
- Format: Personal preference, narrative style

**Target Templates** (`tests/format_to/`):
1. **메타써치 (Meta Search) Template**: Structured format with specific sections
   - 인적사항 (Personal Info): Name, birth year, gender, address, contact
   - 학력사항 (Education): University, degree, GPA
   - 핵심역량 (Core Competencies): Key skills summary
   - 경력사항 (Career Summary): Brief overview
   - 상세경력사항 (Detailed Experience): Full job descriptions

2. **J&J Template**: Company-specific format requirements

3. **AHR Template**: Recruiting company's standardized format

**Example User Queries:**
- "Convert this candidate's resume to the Meta Search format"
- "I'm a headhunter - reformat this resume to match J&J's template"
- "Map my resume content to this company's required template"
- "Take my experience and fit it into the AHR format without losing important details"

**Example Transformation Flow:**

```
SOURCE (문다빈's personal resume):
┌─────────────────────────────────────┐
│ 문다빈                               │
│ Phone: (+82) 10-9860-8431           │
│ Email: dabs.damoon@gmail.com        │
│                                     │
│ 기술                                │
│ - ML/DL Frameworks: PyTorch...      │
│ - Audio Processing: librosa...      │
│                                     │
│ 경력                                │
│ 2023년 7월 - 현재                   │
│ Hudson AI - AI Researcher/Engineer │
│ - 음성합성 알고리즘 개선 연구...     │
│ - TTS 모델 학습 및 추론...          │
└─────────────────────────────────────┘
                 ↓
         [SKILL PROCESSING]
         - Extract personal info
         - Parse work experience
         - Map to template fields
                 ↓
TARGET (Meta Search template filled):
┌─────────────────────────────────────┐
│ 지원분야: AI/ML Engineer            │
│                                     │
│ 인적사항                            │
│ 성    명: 문다빈                    │
│ 연 락 처: 010-9860-8431             │
│           dabs.damoon@gmail.com     │
│                                     │
│ 핵심역량                            │
│ - ML/DL Frameworks (PyTorch...)     │
│ - Audio Processing (librosa...)     │
│                                     │
│ 경력사항 (총 1년 4개월)             │
│ 2023.07 ~ 재직중                    │
│ Hudson AI / AI Researcher/Engineer  │
│                                     │
│ 상세경력사항                        │
│ [AI 연구/개발, 스타트업]            │
│ [주요업무]                          │
│ - 음성합성 알고리즘 개선 연구       │
│ - TTS 모델 학습 및 추론 파이프라인  │
└─────────────────────────────────────┘
```

### Phase 2: Planning Reusable Skill Contents (Step 2 from skill-creator)

#### Edge Cases and Robustness Requirements

Based on industry research, the skill must handle these challenging scenarios:

**Format Variability (Accuracy Targets):**
- Standard chronological resumes: 94-96% accuracy
- Functional/skills-based resumes: 88-92% accuracy
- International resumes: 85-91% accuracy
- Creative/design resumes: 70-82% accuracy
- Scanned paper resumes: 80-88% accuracy
- Academic CVs: 87-93% accuracy

**Complex Visual Elements:**
- Resumes with photos (common in Korean 이력서 format)
- Headers/footers containing critical information (contact details, name)
- Text boxes that ATS/parsers typically ignore
- Graphics, charts, and infographic elements
- Custom banners causing spacing alterations
- Tables and multi-column layouts (2-column, 3-column)

**Non-Standard Structures:**
- Multi-column layouts (left sidebar with skills, main column with experience)
- Table-based resumes vs. paragraph-based resumes
- Non-standard section headings ("Professional Background" vs. "Experience")
- Creative/portfolio-style resumes with unconventional flow
- Mixed Korean-English content
- Resumes with embedded portfolio links, QR codes

**Content Challenges:**
- Varying terminology for same concept (synonyms for skills, job titles)
- Dates in multiple formats (YYYY.MM, YYYY년 MM월, MM/YYYY)
- Missing standard fields (no education section, no skills section)
- Overflow content exceeding template capacity
- Incorrectly formatted data (fake company names as placeholders)
- Cultural variations (Korean age vs. international age)

**Technical Issues:**
- Different file encodings (UTF-8, EUC-KR for Korean text)
- .doc vs .docx format differences
- Scanned PDFs vs. native text PDFs
- Spacing issues (letters separated by spaces appearing as separate words)
- Nested tables or complex cell merges

**Analysis of what's needed repeatedly:**

1. **Content Extraction Guide** (→ references/content_extraction_guide.md)
   - **Multi-source extraction**: Check headers, footers, text boxes, and main body
   - **Personal info extraction**: Name, contact (phone/email), address, photo handling
   - **Experience parsing**: Company, role, dates (multiple formats), responsibilities
   - **Education extraction**: School, degree, dates, GPA, location
   - **Skills identification**: Technical, language, certifications, proficiency levels
   - **Multi-column handling**: Proper reading order (left-to-right, then top-to-bottom)
   - **Table vs. paragraph detection**: Different extraction strategies for each
   - **Section header recognition**: Standardizing non-standard headings using synonyms
   - **Korean-specific elements**: Birth year/age, gender, military service, hobbies
   - **Handling missing sections**: Graceful degradation when standard sections absent

2. **Template Field Mapping Guide** (→ references/template_field_mapping.md)
   - Common template field types and naming conventions
   - Mapping strategies for different template structures
   - Handling missing information gracefully
   - Table-based vs. paragraph-based templates
   - Korean resume conventions (인적사항, 학력사항, 경력사항, etc.)

3. **Quality Preservation Guide** (→ references/quality_preservation.md)
   - Maintaining achievement-focused language during transfer
   - Preserving technical details and metrics
   - Adapting content length to fit template constraints
   - Handling overflow content (when experience exceeds template space)
   - Ensuring professional tone in transformed resume

4. **Resume Parser Script** (→ scripts/resume_parser.py)
   - **File format handling**: .docx, .doc (with proper encoding detection)
   - **Comprehensive extraction**:
     - Main document body (paragraphs, runs, text)
     - Headers and footers (critical for contact info)
     - Tables (with cell merge detection)
     - Text boxes (extract using shape objects)
     - Images (detect photos, extract alt text if present)
   - **Structure detection**:
     - Identify multi-column layouts using position analysis
     - Determine reading order for multi-column content
     - Recognize table-based vs. free-form structures
     - Detect section boundaries and headings
   - **Content normalization**:
     - Date format standardization (YYYY.MM, YYYY년 MM월, MM/YYYY → unified format)
     - Section header synonyms mapping
     - Phone number formatting
     - Text cleanup (extra spaces, formatting artifacts)
   - **Robust error handling**:
     - Handle corrupted or malformed documents
     - Detect and report parsing confidence scores
     - Flag ambiguous or unclear content
   - **Output**: Structured JSON with confidence scores and warnings

5. **Template Mapper Script** (→ scripts/template_mapper.py)
   - **Template analysis**:
     - Identify placeholder fields in template
     - Detect template structure (table-based, paragraph-based, mixed)
     - Recognize field types (text, date, photo, long-form content)
     - Map template fields to standard resume sections
   - **Intelligent mapping**:
     - Match extracted content to template fields using field name matching
     - Handle synonym variations (experience → 경력사항 → work history)
     - Prioritize content when multiple sources available
     - Apply content transformation rules (summarize if needed)
   - **Content fitting**:
     - Detect field length constraints (character limits, cell sizes)
     - Intelligently truncate or summarize overflow content
     - Preserve most important information when space limited
     - Maintain formatting (bold, italic) when possible
   - **Special handling**:
     - Photo insertion for templates requiring photos
     - Table cell population with proper alignment
     - Multi-page handling if template supports it
     - Preserve template styling and fonts
   - **Output**: New .docx file with content mapped to template

6. **Content Validator Script** (→ scripts/content_validator.py)
   - **Completeness check**:
     - Compare extracted content vs. mapped content
     - Identify any dropped or unmapped information
     - Calculate completeness percentage by section
     - Flag critical missing fields (name, contact info)
   - **Quality validation**:
     - Verify dates are properly formatted
     - Check phone/email formatting
     - Validate no text truncation mid-sentence
     - Ensure no garbled text from encoding issues
   - **Template compliance**:
     - Verify all required template fields are populated
     - Check field length constraints are respected
     - Validate formatting consistency
     - Ensure proper table structure maintained
   - **Issue reporting**:
     - Generate detailed validation report
     - Categorize issues by severity (critical, warning, info)
     - Provide specific remediation suggestions
     - Flag low-confidence extractions for manual review
   - **Output**: JSON validation report with pass/fail status and detailed findings

#### Robust Parsing Strategies

To achieve high accuracy across diverse resume formats, implement these strategies:

**1. Multi-Pass Parsing**
- **Pass 1**: Extract from main body (paragraphs, runs)
- **Pass 2**: Extract from tables (with reading order detection)
- **Pass 3**: Extract from headers/footers
- **Pass 4**: Extract from text boxes and shapes
- **Pass 5**: Consolidate and deduplicate information

**2. Template Recognition**
- Use machine learning or rule-based classification to identify common resume templates
- Templates like EfficientNet-B0 can achieve 85%+ accuracy for template identification
- Pre-define extraction rules for known templates (Korean standard, Western standard, creative)
- Fall back to generic extraction for unknown templates

**3. Reading Order Detection**
- For multi-column resumes, analyze text position (x, y coordinates)
- Implement smart reading order: top-to-bottom in left column, then right column
- Handle complex flows (sidebar + main content, header + 2 columns + footer)
- Use visual gap detection to identify column boundaries

**4. Semantic Understanding**
- Use NLP/LLM to understand context even with non-standard headings
- Recognize "Professional Background" as equivalent to "Work Experience"
- Identify job titles, company names, dates through pattern recognition
- Extract skills even when not explicitly labeled as "Skills"

**5. Confidence Scoring**
- Assign confidence scores to each extracted field (0.0 to 1.0)
- High confidence: Found in standard location with clear label
- Medium confidence: Found but location/label unclear
- Low confidence: Inferred from context
- Flag low-confidence extractions for manual review

**6. Graceful Degradation**
- When extraction fails for a section, don't fail entire process
- Return partial results with clear indication of what's missing
- Provide fallback values or placeholders for template mapping
- Generate detailed error report for user review

**7. Korean-Specific Handling**
- Recognize Korean resume conventions (인적사항, 학력사항, 경력사항, 자격사항, etc.)
- Handle mixed Korean-English content appropriately
- Parse Korean date formats (YYYY년 MM월 DD일)
- Extract Korean-specific fields (병역사항/military service, 가족사항/family details)
- Detect and handle both Korean age (한국 나이) and international age

### Phase 3: Initialize the Skill (Step 3 from skill-creator)

Use the skill-creator initialization script:

```bash
cd /Users/dabsdamoon/projects/anthropic-skills/skill-creator
python scripts/init_skill.py resume-formatter --path /Users/dabsdamoon/projects/anthropic-skills
```

This will create the base structure with SKILL.md template and example resource directories.

### Phase 4: Edit the Skill (Step 4 from skill-creator)

#### SKILL.md Structure

**YAML Frontmatter:**
```yaml
---
name: resume-formatter
description: This skill should be used when users request reformatting of a resume to match a specific company template or format. It extracts content from source resumes and maps them to target template structures while preserving content quality. Useful for headhunters, recruiting companies, and applicants who need to fit their resume into company-specific formats.
license: Complete terms in LICENSE.txt
---
```

**Main Sections:**
1. **Overview** - Template-to-template resume conversion
2. **When to Use This Skill** - Headhunters, recruiting companies, applicants with template requirements
3. **Workflow** - Step-by-step process for reformatting
4. **Content Extraction Process** - How to parse source resume
5. **Template Mapping Process** - How to fill target template
6. **Quality Preservation Principles** - Maintain content quality during transformation
7. **Handling Edge Cases** - Missing info, overflow content, format mismatches
8. **Output Requirements** - Completeness validation and final deliverable

#### Writing Style (from skill-creator guidelines)
- Use imperative/infinitive form (verb-first instructions)
- Objective, instructional language
- "To accomplish X, do Y" rather than "You should do X"

#### Content Focus
Following skill-creator principles:
- Include information that would be beneficial and non-obvious to Claude
- Focus on procedural knowledge and domain-specific details
- Reference bundled resources (scripts, references, assets) so Claude knows how to use them

### Phase 5: Create Bundled Resources

#### references/format_types.md
Detailed guide on:
- Chronological format: Timeline-based, most common
- Functional/Skills-based format: Organized by skill categories
- Hybrid/Combination format: Mix of chronological and functional
- Targeted format: Customized for specific job posting
- Mini/One-page format: Condensed version
- Infographic format: Visual/creative presentation

#### references/industry_conventions.md
Industry-specific best practices for:
- Technology & Software Engineering
- Finance & Consulting
- Healthcare & Medical
- Academic & Research
- Creative & Design
- Sales & Marketing
- Legal
- Engineering (non-software)

#### references/ats_optimization.md
Guidelines for:
- How ATS systems parse resumes
- Keywords and formatting that work well
- Common parsing failures (tables, headers, graphics)
- Testing with ATS simulation tools
- Balancing human-readability with ATS-compatibility

#### scripts/format_converter.py
Python script to:
- Read .docx files using python-docx
- Generate LaTeX using template substitution
- Convert to markdown using clean formatting
- Export to PDF using reportlab or similar
- Handle special characters and formatting preservation

#### scripts/ats_analyzer.py
Python script to:
- Parse resume content
- Check for ATS-friendly formatting
- Identify keywords relevant to job descriptions
- Generate compatibility score
- Provide actionable recommendations

#### assets/templates/
Create 5+ professionally designed templates:
- chronological_template.docx - Traditional timeline format
- functional_template.docx - Skills-focused format
- hybrid_template.docx - Combined approach
- tech_resume_template.docx - Tech industry optimized
- academic_cv_template.docx - Academic/research focused

Each template should:
- Use ATS-friendly formatting
- Include placeholder text with examples
- Be customizable and clean
- Follow modern design principles

#### assets/examples/
Create before/after examples showing:
- Chronological → Functional transformation
- Academic CV → Industry resume transformation
- Traditional → Modern design update
- Generic → ATS-optimized transformation

### Phase 6: Testing with Edge Cases

Before packaging, thoroughly test the skill with diverse resume formats:

**Test Suite Categories:**

1. **Standard Formats** (Target: 94-96% accuracy)
   - Simple chronological, single-column
   - Table-based Korean standard format
   - Western-style bullet-point format

2. **Complex Layouts** (Target: 85-92% accuracy)
   - Two-column layouts (sidebar + main)
   - Three-column layouts
   - Mixed table and paragraph format
   - Creative templates with non-standard flow

3. **Edge Cases** (Target: 70-85% accuracy)
   - Headers/footers with critical info
   - Text boxes containing skills or summary
   - Resumes with photos
   - Multi-page resumes
   - Scanned/PDF resumes (if supported)

4. **Content Challenges**
   - Missing sections (no education, no skills)
   - Non-standard section headings
   - Mixed Korean-English content
   - Overflow content (very long experience section)
   - Minimal content (entry-level, 1 job)

5. **Language/Encoding**
   - Pure Korean resumes
   - Pure English resumes
   - Mixed Korean-English
   - Special characters and formatting
   - Different file encodings (UTF-8, EUC-KR)

**Validation Criteria:**
- ✓ All critical fields extracted (name, contact, experience)
- ✓ Content properly mapped to target template
- ✓ No garbled text or encoding issues
- ✓ Validation report shows >90% completeness
- ✓ Manual review confirms quality

**Create Test Cases:**
- Document each test case with source resume type
- Record expected extraction results
- Compare actual vs. expected
- Iterate on parser/mapper scripts until passing
- Build regression test suite

### Phase 7: Packaging (Step 5 from skill-creator)

Once complete, package the skill:

```bash
cd /Users/dabsdamoon/projects/anthropic-skills/skill-creator
python scripts/package_skill.py /Users/dabsdamoon/projects/anthropic-skills/resume-formatter
```

This will:
1. Validate the skill (YAML format, naming, descriptions, etc.)
2. Create a distributable .zip file
3. Report any validation errors

### Phase 7: Iteration (Step 6 from skill-creator)

After testing:
1. Use the skill on real resume transformation tasks
2. Notice any struggles or inefficiencies
3. Identify improvements to SKILL.md or bundled resources
4. Implement changes and test again
5. Gather user feedback

## Key Design Principles

Following the skill-creator guidance:

### Progressive Disclosure
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude

### Avoid Duplication
- Information lives in either SKILL.md or references, not both
- Keep SKILL.md lean - detailed reference material goes in references/
- Only essential procedural instructions in SKILL.md

### Quality Focus
- Clear, specific metadata so Claude knows when to use the skill
- Comprehensive but concise SKILL.md
- Well-documented scripts that can be executed without reading into context
- Professional, usable templates and examples

## Success Criteria

The skill will be successful when:

**Accuracy Benchmarks:**
1. Standard chronological resumes: ≥94% extraction accuracy
2. Complex multi-column resumes: ≥85% extraction accuracy
3. Edge cases (headers/footers/text boxes): ≥70% extraction accuracy
4. Overall completeness: ≥90% of source content mapped to target

**Functionality:**
5. Successfully handles 10+ different resume layout types
6. Extracts content from headers, footers, tables, text boxes, and main body
7. Properly handles Korean, English, and mixed-language resumes
8. Gracefully handles missing sections and overflow content
9. Generates detailed validation reports with confidence scores

**Quality:**
10. No garbled text or encoding issues
11. Proper date format standardization
12. Professional formatting maintained in output
13. Critical information never lost (name, contact, experience)

**Usability:**
14. Clear error messages when parsing fails
15. Detailed validation reports help users understand what was extracted
16. Saves headhunters/recruiters significant time vs. manual reformatting
17. Works with user-provided templates (not just built-in ones)

## Differences from resume-translator

**resume-translator (existing):**
- Focuses on **language translation** (English ↔ Japanese/Korean/Chinese)
- Maintains or adapts cultural conventions for target language region
- Emphasizes translation quality and achievement-focused language
- Has references for region-specific resume practices (Japanese 履歴書, Korean 이력서, etc.)
- Output: Same resume with translated content

**resume-formatter (new):**
- Focuses on **template conversion** (source format → company template)
- Extracts content and maps to specific template structure
- Works within same language (Korean → Korean, English → English)
- Emphasizes content preservation and field mapping
- Has parsing scripts, mapping guides, and validation tools
- Output: Content fitted into company-required template

Both skills can work together:
1. **Scenario 1**: Translate English resume to Korean (resume-translator) → Reformat to Meta Search template (resume-formatter)
2. **Scenario 2**: Reformat to J&J template (resume-formatter) → Translate to English version (resume-translator)

## Next Steps

1. Review this plan with user for feedback
2. Ask clarifying questions about specific use cases
3. Initialize the skill using init_skill.py
4. Implement SKILL.md following the structure above
5. Create bundled resources (references, scripts, templates)
6. Validate and package the skill
7. Test with real resume transformation scenarios
8. Iterate based on feedback

## Questions for User

Before proceeding with implementation:

1. **Scope confirmation**: Does this updated plan match your vision? The skill now focuses on:
   - Extracting content from applicant's personal resume format
   - Mapping to company-specific template (like Meta Search, J&J, AHR examples)
   - Preserving all information during transformation

2. **Template handling**: How should the skill handle target templates?
   - Option A: User provides both source resume + target template file
   - Option B: Skill includes common company templates in assets/
   - Option C: Both - allow custom templates but also include popular ones

3. **Missing information**: How to handle when source resume lacks fields required by template?
   - Leave blank with placeholder text?
   - Ask user for missing info?
   - Mark clearly as "정보 없음" or "N/A"?

4. **Overflow content**: When experience is too long for template fields?
   - Intelligently summarize?
   - Ask user which parts to prioritize?
   - Create supplementary section?

5. **Language support**:
   - Primary focus on Korean resumes?
   - Should it also handle English resumes?
   - Mixed language resumes (Korean + English)?

6. **Script automation level**:
   - Fully automated parsing and mapping?
   - Semi-automated with human review checkpoints?
   - What's the acceptable error rate?

7. **Testing**: The test files you have - can I use those for:
   - Developing the parsing logic?
   - Creating before/after examples in the skill documentation?
   - Validating the transformation quality?
