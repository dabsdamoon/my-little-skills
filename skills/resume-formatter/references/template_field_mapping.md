# Template Field Mapping Guide

This guide provides strategies for mapping extracted resume content to various template structures.

## Common Template Types

### 1. Korean Standard Table-Based Template

**Structure**: Tables with field labels and value cells

**Example** (Meta Search format):
```
┌────────────────────────────────────────────┐
│ 지원분야: [Application Field]              │
├────────────────────────────────────────────┤
│ 인적사항                                   │
├──────────┬─────────────────────────────────┤
│ 성    명 │ [Name]                          │
├──────────┼─────────────────────────────────┤
│ 생년/성별│ [Birth Year] / [Gender]         │
├──────────┼─────────────────────────────────┤
│ 주    소 │ [Address]                       │
├──────────┼─────────────────────────────────┤
│ 연 락 처 │ [Phone] / [Email]               │
└──────────┴─────────────────────────────────┘
```

**Field Mapping**:
| Template Field | Maps To | Notes |
|---------------|---------|-------|
| 성명 (Name) | personal_info.name | Direct mapping |
| 생년/성별 (Birth/Gender) | personal_info.birth_date, personal_info.gender | Combine two fields |
| 주소 (Address) | personal_info.address | Full address |
| 연락처 (Contact) | personal_info.phone, personal_info.email | Combine with "/" separator |
| 학력사항 (Education) | education[] | Map all education entries |
| 경력사항 (Career) | experience[] | Summary of experience |
| 상세경력사항 (Detailed Career) | experience[] | Full descriptions |
| 핵심역량 (Core Competencies) | skills.technical | Top skills |

### 2. Western Chronological Template

**Structure**: Sections with headings, bullet points

**Example**:
```
[NAME]
[Contact Info]

PROFESSIONAL SUMMARY
[2-3 sentences]

EXPERIENCE
Company | Title | Dates
• Achievement 1
• Achievement 2

EDUCATION
University | Degree | Year

SKILLS
Category: skill1, skill2, skill3
```

**Field Mapping**:
| Template Section | Maps To | Notes |
|-----------------|---------|-------|
| Name (header) | personal_info.name | Large font |
| Contact (header) | personal_info.phone, email, address | Line-separated |
| Professional Summary | summary OR derived from experience | 2-3 sentences |
| Experience | experience[] | Chronological order |
| Education | education[] | Reverse chronological |
| Skills | skills.technical | Grouped by category |

### 3. Functional/Skills-Based Template

**Structure**: Skills emphasized, experience minimized

**Example**:
```
[NAME]
[Contact]

CORE COMPETENCIES
• Skill area 1
• Skill area 2
• Skill area 3

PROFESSIONAL EXPERIENCE
Brief company/title/dates list

EDUCATION
[Standard format]
```

**Field Mapping**:
| Template Section | Maps To | Notes |
|-----------------|---------|-------|
| Core Competencies | skills.technical + derived from experience | Group skills by area |
| Professional Experience | experience[] | Brief format, no details |
| Technical Skills | skills.technical | Detailed list |

## Field Type Identification

### Short Text Fields
**Characteristics**:
- Single line
- Limited characters (typically 50-100)
- Examples: Name, Title, Company

**Mapping Strategy**:
- Direct copy if fits
- Truncate with "..." if too long
- No line breaks

### Long Text Fields
**Characteristics**:
- Multiple paragraphs allowed
- Character limit 500-2000
- Examples: Job description, Summary

**Mapping Strategy**:
- Copy full content if fits
- Intelligent summarization if too long
- Preserve paragraph breaks

### Date Fields
**Characteristics**:
- Specific format required
- Examples: MM/YYYY, YYYY.MM, YYYY년 MM월

**Mapping Strategy**:
- Detect template date format
- Convert extracted dates to match
- Handle "Present" / "현재" / "재직중"

### List Fields
**Characteristics**:
- Bullet points or comma-separated
- Examples: Skills, Responsibilities

**Mapping Strategy**:
- Match list format (bullets vs commas)
- Maintain or convert formatting
- Limit number of items if constrained

### Photo Fields
**Characteristics**:
- Image placeholder
- Specific dimensions
- Examples: 3x4cm, 35x45mm

**Mapping Strategy**:
- Insert photo if available
- Resize to match dimensions
- Leave blank if no photo

## Synonym Mapping

### Experience Section Synonyms

**Korean**:
- 경력사항 (Gyeongryeoksahang)
- 경력 (Gyeongryeok)
- 경력 개요 (Gyeongryeok Gaejo)
- 상세경력사항 (Sangsegyeongryeoksahang)
- 직장 경력 (Jikjang Gyeongryeok)
- 근무 경력 (Geunmu Gyeongryeok)

**English**:
- Experience
- Work Experience
- Professional Experience
- Employment History
- Career History
- Work History
- Professional Background
- Career Synopsis

**All map to**: `experience[]`

### Education Section Synonyms

**Korean**:
- 학력사항 (Hakryeoksahang)
- 학력 (Hakryeok)
- 교육사항 (Gyoyuksahang)

**English**:
- Education
- Academic Background
- Educational Background
- Academic History
- Qualifications

**All map to**: `education[]`

### Skills Section Synonyms

**Korean**:
- 핵심역량 (Haeksimyeokryang)
- 보유기술 (Boyugisul)
- 전문기술 (Jeonmungisul)
- 기술스택 (Gisulseuta-ek)
- 보유역량 (Boyuyeokryang)

**English**:
- Skills
- Technical Skills
- Core Competencies
- Expertise
- Proficiencies
- Competencies
- Technical Proficiencies

**All map to**: `skills[]`

## Template-Specific Mapping Examples

### Example 1: Meta Search Template

**Template Structure**:
```
지원분야: [Position applying for]

인적사항 (Personal Information)
- 성명: [Name]
- 생년/성별: [Birth Year] / [Gender]
- 주소: [Address]
- 연락처: [Phone] / [Email]

학력사항 (Education)
[Date Range] [School] [Degree] [Major] [GPA]

핵심역량 (Core Competencies)
- [Competency 1]
- [Competency 2]

경력사항 (Career Summary)
[Date Range] [Company] / [Department] / [Title]

상세경력사항 (Detailed Experience)
[Date Range]
[Company] / [Department] / [Title]
[Company Description]
[주요업무]
- [Responsibility 1]
- [Responsibility 2]
```

**Mapping Logic**:

**지원분야 (Application Field)**:
- Extract from: Job title or user input
- Fallback: Most recent job title

**인적사항 (Personal Information)**:
- 성명: `personal_info.name`
- 생년/성별: `f"{personal_info.birth_year}년 생 / {personal_info.gender}"`
  - If birth_year missing: Ask user or leave blank
  - If gender missing: Leave blank or use "비공개"
- 주소: `personal_info.address`
- 연락처: `f"{personal_info.phone} / {personal_info.email}"`

**학력사항 (Education)**:
- Format: `[Start.End] [School] [Degree] [Major] (Location) (GPA/Total)`
- Example: `2015.03 ~ 2019.02 서울대학교 컴퓨터공학 학사 (서울) (3.8/4.0)`

**핵심역량 (Core Competencies)**:
- Extract top 3-5 skills from `skills.technical`
- Or derive from experience achievements
- Format as bullet points

**경력사항 (Career Summary)**:
- One line per job: `[Dates] [Company] / [Department] / [Title]`
- Example: `2023.07 ~ 재직중 Hudson AI / AI Research / AI Researcher`

**상세경력사항 (Detailed Experience)**:
- Full block per job
- Include company description: `[Industry, Company Size, Revenue]`
- [주요업무] section with bullet points
- Preserve quantified achievements

### Example 2: Simple Western Template

**Template Structure**:
```
NAME
Phone | Email | LinkedIn

SUMMARY
[2-3 sentences]

EXPERIENCE
Company Name, Location | Job Title | Dates
• Achievement 1
• Achievement 2

EDUCATION
University Name | Degree, Major | Graduation Year

SKILLS
Technical: [comma-separated]
Languages: [comma-separated]
```

**Mapping Logic**:

**Header**:
- Name: `personal_info.name` (18-24pt font)
- Contact line: `{phone} | {email} | {linkedin}`

**Summary**:
- If exists: Use extracted summary
- If not: Generate from most recent role
  - Template: "[Title] with [X] years of experience in [domain]. Expertise in [key skills]. Achieved [top achievement]."

**Experience**:
- Format: `[Company], [Location] | [Title] | [Start] - [End]`
- Bullets: Extract from responsibilities
- Limit: Top 4-5 bullets per role
- Preserve metrics and achievements

**Education**:
- Format: `[University] | [Degree], [Major] | [Year]`
- Include GPA if >= 3.5/4.0
- Reverse chronological order

**Skills**:
- Technical: Comma-separated list from `skills.technical`
- Languages: From `skills.languages` with proficiency

## Handling Missing Information

### Critical Fields (Must Have)

| Field | If Missing | Action |
|-------|-----------|--------|
| Name | Always required | **ASK USER** - Cannot proceed without |
| Contact (Phone or Email) | At least one required | **ASK USER** - Critical for contact |
| Experience | Required for most templates | **ASK USER** if no experience/projects found |

### Important Fields (Should Have)

| Field | If Missing | Action |
|-------|-----------|--------|
| Education | Common but not always required | Use placeholder "정보 없음" or leave blank |
| Address | Often optional in modern resumes | Leave blank or use "Available upon request" |
| Photo | Required in some Korean templates | Leave placeholder or **ASK USER** if required |

### Optional Fields (Nice to Have)

| Field | If Missing | Action |
|-------|-----------|--------|
| Summary | Can be derived | Generate from experience if needed |
| Skills section | Can be derived | Extract from experience descriptions |
| Certifications | Not always present | Leave blank |
| Military Service | Korean male only | Leave blank for others |
| GPA | Often omitted | Leave blank |

## Content Fitting Strategies

### When Content Exceeds Field Limit

**Strategy 1: Intelligent Truncation**
```
Original (200 chars):
"Developed and deployed machine learning models achieving 95% accuracy using PyTorch and TensorFlow, while leading a cross-functional team of 5 engineers and reducing system latency by 40% through optimization."

Truncated (100 chars):
"Led ML model development achieving 95% accuracy and reduced latency 40% using PyTorch/TensorFlow."
```

**Prioritization**:
1. Quantified achievements (95% accuracy, 40% reduction)
2. Action verbs (Developed, Led)
3. Technical specifics (PyTorch, TensorFlow)
4. Team/scale info (team of 5) - can be dropped if needed

**Strategy 2: Bullet Point Reduction**
```
Original (10 bullets per job):
• Achievement 1
• Achievement 2
...
• Achievement 10

Reduced (4 bullets):
• Top achievement with metrics
• Second achievement with impact
• Technical accomplishment
• Leadership/team contribution
```

**Selection criteria**:
- Keep most recent accomplishments
- Preserve quantified results
- Maintain technical diversity
- Show progression/growth

**Strategy 3: Summarization**
```
Original (5 short-term roles):
- Company A (3 months)
- Company B (4 months)
- Company C (2 months)
- Company D (6 months)
- Company E (3 months)

Summarized:
"Freelance Consulting (18 months total): Projects with Companies A-E focusing on [domain]. Key achievements: [top 2 results]."
```

### Multi-Page Considerations

**If template is single-page only**:
1. Prioritize recent experience (last 3-5 years)
2. Condense older roles
3. Remove less relevant projects
4. Keep education brief
5. Limit skills to top 8-10

**If template allows multiple pages**:
1. Page 1: Contact, Summary, Recent experience (2-3 roles)
2. Page 2: Additional experience, Education, Skills, Certifications
3. Maintain consistent formatting across pages

## Field Length Guidelines

### Typical Field Constraints

| Field Type | Typical Limit | Handling |
|-----------|--------------|----------|
| Name | 50 chars | Usually fits; truncate if compound names |
| Job Title | 80 chars | Shorten if needed (Sr. SWE → Senior Software Engineer) |
| Company Name | 100 chars | Usually fits; use acronym if very long |
| Summary | 300-500 chars | Summarize to 2-3 sentences max |
| Experience bullet | 150-200 chars each | One sentence per bullet, prioritize metrics |
| Skills list | 500 chars | Top 10-15 skills, comma-separated |
| Education entry | 200 chars | School, degree, year, GPA (if good) |

### Character Count Estimation

```python
def estimate_field_length(template_field):
    """Estimate how much content fits in a field"""
    # For table cells
    if is_table_cell:
        # Approximate: 10-12 chars per cm of width
        width_cm = get_cell_width_cm()
        return width_cm * 11

    # For text fields
    if has_char_limit:
        return specified_limit

    # Default based on field type
    defaults = {
        'name': 50,
        'title': 80,
        'summary': 400,
        'bullet': 180,
        'skill_list': 500
    }
    return defaults.get(field_type, 200)
```

## Template Analysis Algorithm

**Step 1: Identify Structure**
```python
def analyze_template(doc):
    structure = {
        'type': None,  # 'table', 'paragraph', 'mixed'
        'fields': [],
        'sections': []
    }

    # Check for tables
    if len(doc.tables) > 0:
        structure['type'] = 'table'
        structure['fields'] = extract_table_fields(doc.tables)
    else:
        structure['type'] = 'paragraph'
        structure['sections'] = detect_sections(doc.paragraphs)

    return structure
```

**Step 2: Extract Field Names**
```python
def extract_table_fields(tables):
    fields = []
    for table in tables:
        for row in table.rows:
            # Typically: First cell = field name, Second cell = value placeholder
            if len(row.cells) >= 2:
                field_name = row.cells[0].text.strip()
                field_type = infer_field_type(row.cells[1])
                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'cell': row.cells[1]
                })
    return fields
```

**Step 3: Map to Standard Fields**
```python
def map_to_standard(field_name):
    """Map template field name to standard extracted field"""
    mapping = {
        '성명': 'personal_info.name',
        'Name': 'personal_info.name',
        '연락처': 'personal_info.contact',
        'Phone': 'personal_info.phone',
        'Email': 'personal_info.email',
        '경력사항': 'experience',
        'Experience': 'experience',
        # ... extensive mapping dictionary
    }

    # Try exact match
    if field_name in mapping:
        return mapping[field_name]

    # Try fuzzy match
    for key, value in mapping.items():
        if key.lower() in field_name.lower():
            return value

    return None  # Unknown field
```

## Common Template Variations

### Korean Company Templates

**Samsung Format** (hypothetical - adapt as needed):
- Strong emphasis on education (listed first)
- Detailed family information section
- Photo required (top right)
- Military service mandatory for males

**LG Format** (hypothetical):
- Skills section prominent
- Project experience separate from employment
- Language proficiency with test scores
- Hobbies/interests section

### Western Templates

**Tech Company** (Google, Meta style):
- Projects and GitHub links emphasized
- Education minimal (school, degree, year only)
- Skills categorized (Languages, Frameworks, Tools, etc.)
- Impact metrics critical

**Consulting** (McKinsey, BCG style):
- Education prominent (GPA required if high)
- Quantified achievements essential
- Leadership and teamwork emphasized
- Structured problem-solving examples

**Finance** (Goldman, JP Morgan style):
- GPA and school prestige important
- Certifications (CFA, etc.) prominent
- Quantified financial impact
- Conservative formatting

## Validation After Mapping

**Check**:
1. All required fields populated
2. No placeholder text remaining (unless intentional)
3. Date formats consistent
4. No text overflow (truncated mid-sentence)
5. Formatting maintained (bold, bullets, etc.)
6. Photo inserted if required
7. No encoding errors (Korean characters display correctly)

**Generate report**:
```
Mapping Completeness: 95%

Populated Fields:
✓ Personal Info (100%)
✓ Experience (95% - truncated oldest role)
✓ Education (100%)
✓ Skills (90% - limited to top 10)

Missing/Incomplete:
⚠ Photo not found in source
⚠ Military service info not available
⚠ GPA not specified

Modifications Made:
• Summarized experience bullets (10 → 5 per role)
• Truncated skills list (20 → 10 items)
• Formatted dates to YYYY.MM format
```
