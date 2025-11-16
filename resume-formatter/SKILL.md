---
name: resume-formatter
description: This skill should be used when users request reformatting of a resume to match a specific company template or format. It extracts content from source resumes and maps them to target template structures while preserving content quality. Useful for headhunters, recruiting companies, and applicants who need to fit their resume into company-specific formats.
license: Complete terms in LICENSE.txt
---

# Resume Formatter

## Overview

To reformat resumes from one template to another, use this skill. The skill extracts content from a source resume (applicant's personal format) and intelligently maps it to a target template (company-required format) while preserving all important information.

**Primary Use Cases:**
- Headhunters reformatting candidate resumes to match client company requirements
- Recruiting companies standardizing applicant resumes to internal templates
- Job applicants adapting their resume to company-specific template requirements

**Robustness**: This skill handles diverse resume formats including multi-column layouts, headers/footers, text boxes, tables, mixed languages, and non-standard structures.

## When to Use This Skill

Use this skill when:
- User provides both a source resume and target template
- User requests conversion to a specific company format (e.g., "Convert to Meta Search format")
- Headhunter needs to reformat multiple candidate resumes to client standards
- Applicant wants to fit their resume into a required template

**Keywords**: resume reformatting, template conversion, resume mapping, format adaptation, headhunter tools, recruiting templates, 이력서 변환, template matching

## Workflow

Follow this process to reformat a resume:

### Step 1: Gather Input

**Collect from user:**
1. **Source resume**: Applicant's resume file (.docx or .doc)
2. **Target template**: Company template file (.docx or .doc) OR template name if using built-in templates
3. **Special instructions**: Any fields to prioritize, missing information, or preferences

**Validate inputs:**
- Verify source resume is readable (.docx or .doc format)
- Verify target template is accessible
- Confirm both files contain expected content (not corrupted)

### Step 2: Extract Content from Source Resume

Use the `scripts/resume_parser.py` script to extract structured content.

**Extraction process:**
1. **Parse document comprehensively**:
   - Main body content (paragraphs, runs, text)
   - Tables (with proper cell reading order)
   - Headers and footers (often contain contact info)
   - Text boxes and shapes (may contain skills summaries)
   - Images (detect photos for templates requiring them)

2. **Identify sections** using multiple strategies:
   - Standard headings (Experience, Education, Skills, etc.)
   - Korean standard headings (인적사항, 학력사항, 경력사항, 핵심역량, etc.)
   - Synonym recognition (Professional Background → Experience)
   - Context-based section detection when headings unclear

3. **Extract structured data**:
   - **Personal Information**: Name, phone, email, address, photo
   - **Experience**: Company, role, dates, responsibilities/achievements
   - **Education**: School, degree, graduation date, GPA, location
   - **Skills**: Technical skills, languages, certifications, proficiency levels
   - **Additional**: Summary, projects, publications, awards, military service (Korean), hobbies

4. **Handle complex layouts**:
   - For multi-column resumes: Analyze text positions to determine reading order
   - For table-based resumes: Extract cell-by-cell while maintaining relationships
   - For mixed formats: Combine extraction strategies

5. **Normalize content**:
   - Standardize date formats (YYYY.MM, YYYY년 MM월, MM/YYYY → unified format)
   - Clean phone number formatting
   - Remove formatting artifacts and extra whitespace
   - Handle encoding issues (UTF-8, EUC-KR for Korean)

**Output**: Structured JSON containing all extracted content with confidence scores

**Refer to** `references/content_extraction_guide.md` for detailed extraction strategies.

### Step 3: Analyze Target Template

**Understand template structure:**
1. **Identify template type**:
   - Table-based (Korean standard)
   - Paragraph-based (Western standard)
   - Mixed format

2. **Detect placeholder fields**:
   - Locate where content should be inserted
   - Identify field types (short text, long text, date, photo, etc.)
   - Determine field constraints (character limits, cell sizes)

3. **Map template sections to standard resume sections**:
   - 인적사항 (Personal Info) → name, contact, address, photo
   - 학력사항 (Education) → schools, degrees, dates
   - 경력사항 (Career Summary) → brief overview of experience
   - 상세경력사항 (Detailed Experience) → full job descriptions
   - 핵심역량 (Core Competencies) → key skills

**Refer to** `references/template_field_mapping.md` for common template structures.

### Step 4: Map Content to Template

Use the `scripts/template_mapper.py` script to populate the target template.

**Mapping process:**
1. **Field matching**:
   - Match extracted content to template fields using field names
   - Handle synonym variations (experience ↔ 경력사항 ↔ work history)
   - Prioritize content when multiple sources available

2. **Content transformation**:
   - **Fit to constraints**: Truncate or summarize if content exceeds field limits
   - **Preserve quality**: Maintain achievement-focused language and key metrics
   - **Intelligent summarization**: When overflow occurs, prioritize:
     - Quantified achievements and business impact
     - Recent and relevant experience
     - Technical skills and certifications
     - Key responsibilities

3. **Special handling**:
   - **Photos**: Extract from source, resize to template requirements, insert in designated location
   - **Tables**: Populate cells maintaining proper alignment
   - **Dates**: Format according to template conventions
   - **Multi-page**: If template supports, use multiple pages; otherwise consolidate

4. **Format preservation**:
   - Maintain bold, italic, and other text styling when possible
   - Preserve bullet points and list structures
   - Keep template's original fonts and styling

**Refer to** `references/quality_preservation.md` for content quality guidelines.

### Step 5: Validate Completeness

Use the `scripts/content_validator.py` script to verify transformation quality.

**Validation checks:**
1. **Completeness**:
   - Compare extracted content vs. mapped content
   - Calculate completeness percentage per section
   - Flag any unmapped or dropped information
   - Verify critical fields populated (name, contact, experience)

2. **Quality**:
   - Verify dates properly formatted
   - Check phone/email formatting correct
   - Ensure no text truncated mid-sentence
   - Validate no garbled text from encoding issues

3. **Template compliance**:
   - Confirm all required template fields populated
   - Verify field length constraints respected
   - Validate formatting consistency
   - Check proper table structure maintained

**Output**: Validation report with:
- Overall completeness score (target: ≥90%)
- Per-section completeness
- List of issues by severity (critical, warning, info)
- Specific recommendations for manual review
- Low-confidence extractions flagged

### Step 6: Review and Finalize

**Present to user:**
1. **Filled template**: The reformatted resume in target template format
2. **Validation report**: Completeness scores and any issues found
3. **Recommendations**: Fields requiring manual review or missing information

**Ask user to verify:**
- Critical information accuracy (name, contact, dates)
- Content completeness (nothing important dropped)
- Fields flagged as low-confidence
- Any missing information that should be added

**Make adjustments** based on user feedback:
- Add missing information user provides
- Correct any mis-mapped content
- Adjust summarization if needed
- Re-validate after changes

## Handling Edge Cases

### Missing Information

When source resume lacks fields required by template:
1. **Leave placeholder text**: Use template's original placeholder (e.g., "OOO", "N/A")
2. **Mark clearly**: In Korean templates use "정보 없음", in English use "Not Provided"
3. **Ask user**: Prompt for missing critical information (name, contact)
4. **Flag in validation report**: List all missing required fields

### Overflow Content

When experience is too long for template fields:
1. **Intelligent summarization**:
   - Keep most recent and relevant positions
   - Preserve quantified achievements
   - Maintain technical skills and impact metrics
   - Condense older/less relevant experience

2. **Priority ranking**:
   - Recent roles (last 3-5 years) get full detail
   - Older roles get condensed summaries
   - Achievements with metrics always preserved
   - Generic descriptions removed first

3. **User consultation**: If unclear what to prioritize, ask user

### Complex Layouts

For challenging source resume formats:
1. **Multi-column layouts**:
   - Analyze text positions (x, y coordinates)
   - Determine proper reading order
   - Extract left column, then right column (or vice versa based on layout)

2. **Headers/footers with critical info**:
   - Always check headers/footers first
   - Extract contact information even if in header
   - Don't rely only on main body content

3. **Text boxes**:
   - Access document shapes and text boxes explicitly
   - Extract content that standard parsing misses
   - Merge with main body content appropriately

4. **Tables**:
   - Detect table-based resume structure
   - Extract cell-by-cell maintaining row relationships
   - Handle merged cells properly

### Non-Standard Section Headings

When sections use unusual headings:
1. **Synonym matching**: Use mapping dictionary (Professional Background → Experience)
2. **Context detection**: Analyze content to infer section type
3. **LLM understanding**: Use semantic understanding to classify unclear sections
4. **Flag uncertainty**: Mark low-confidence section classifications

### Date Format Variations

Normalize all date formats:
- Input: 2023년 7월, 2023.07, July 2023, 07/2023
- Output: Format matching template convention (typically YYYY.MM or YYYY년 MM월)

### Language Mixing

For resumes with mixed Korean-English content:
1. **Preserve original language**: Don't translate during reformatting
2. **Maintain context**: Keep Korean and English content together appropriately
3. **Format consistently**: Apply template's language conventions

### Low Confidence Extractions

When parser confidence is low (<0.7):
1. **Flag in validation report**: List all low-confidence fields
2. **Request manual review**: Ask user to verify these specific fields
3. **Provide context**: Show what was extracted and why confidence is low
4. **Offer alternatives**: If multiple interpretations possible, present options

## Quality Preservation Principles

Throughout the reformatting process, maintain these quality standards:

**1. Achievement-Focused Language**
- Preserve quantified achievements and metrics
- Maintain strong action verbs (Architected, Developed, Led)
- Keep business impact statements (revenue, efficiency, scale)
- Don't dilute accomplishments when summarizing

**2. Technical Precision**
- Preserve specific technical terminology
- Keep exact tool/framework names (PyTorch, AWS, etc.)
- Maintain version numbers and certifications
- Don't generalize technical details

**3. Professional Tone**
- Ensure all content maintains professional register
- Remove casual language if present
- Standardize formatting consistently
- Fix any grammatical issues noticed

**4. Completeness**
- Never drop critical information (contact, major roles, education)
- Flag if information must be omitted due to space constraints
- Prioritize recent/relevant experience over older/less relevant
- Always preserve name, contact info, and recent experience

## Output Requirements

After completing the reformatting, provide:

**1. Reformatted Resume File**
- New .docx file with content mapped to target template
- Filename: `[original_name]_[template_name]_formatted.docx`
- Professional formatting maintained
- All template fields properly populated

**2. Validation Report**
- Overall completeness score
- Per-section breakdown
- List of issues/warnings
- Fields requiring manual review
- Missing information summary

**3. Summary for User**
- Brief description of what was done
- Any decisions made (summarization, prioritization)
- Items requiring user verification
- Suggestions for improvement

**Example summary:**
```
Reformatted resume for 문다빈 to Meta Search template format.

Completeness: 92%

Key transformations:
- Extracted personal info from header
- Mapped technical skills to 핵심역량 section
- Consolidated 3 years of experience into 상세경력사항
- Preserved all quantified achievements

Please review:
- 학력사항: GPA not found in source resume
- 병역사항: Military service information not available
- Contact address: Currently showing old address from source

File: 문다빈_MetaSearch_formatted.docx
```

## Resources

### scripts/

**resume_parser.py** - Robust content extraction
- Extracts from main body, headers, footers, tables, text boxes
- Handles multi-column layouts with reading order detection
- Normalizes dates, phone numbers, formatting
- Returns structured JSON with confidence scores

**template_mapper.py** - Intelligent content mapping
- Analyzes template structure and placeholder fields
- Maps extracted content to template using field matching
- Handles overflow with intelligent summarization
- Inserts photos, populates tables, maintains formatting

**content_validator.py** - Quality validation
- Compares source vs. target for completeness
- Validates formatting and field constraints
- Generates detailed report with severity levels
- Flags low-confidence extractions for review

### references/

**content_extraction_guide.md** - Detailed extraction strategies for:
- Multi-source extraction (headers, footers, text boxes, main body)
- Multi-column layout handling
- Table vs. paragraph detection
- Section header recognition and synonyms
- Korean-specific elements (age, military service, etc.)

**template_field_mapping.md** - Template structure guidance for:
- Common field types and naming conventions
- Korean resume standard sections
- Mapping strategies for different template structures
- Handling missing fields gracefully

**quality_preservation.md** - Content quality guidelines for:
- Maintaining achievement-focused language
- Preserving technical precision
- Adapting content length to constraints
- Professional tone throughout
