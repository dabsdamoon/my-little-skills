# Content Extraction Guide

This guide provides detailed strategies for extracting content from diverse resume formats.

## Multi-Source Extraction Strategy

Resume content can appear in multiple locations. Check all sources:

### 1. Main Document Body
**Standard location** for most content.

**Extraction method**:
```python
from docx import Document
doc = Document('resume.docx')

for paragraph in doc.paragraphs:
    text = paragraph.text
    # Process paragraph text
```

**What to extract**:
- Section headings
- Job descriptions
- Education details
- Skills lists
- Summary/objective statements

### 2. Headers and Footers
**Critical location** - often contains contact information that gets missed.

**Extraction method**:
```python
# Check all headers
for section in doc.sections:
    header = section.header
    for paragraph in header.paragraphs:
        text = paragraph.text
        # Extract contact info

# Check all footers
for section in doc.sections:
    footer = section.footer
    for paragraph in footer.paragraphs:
        text = paragraph.text
        # Extract portfolio links, page numbers
```

**What to extract**:
- Name (often in header)
- Phone number, email (commonly in header)
- Portfolio/LinkedIn links (sometimes in footer)
- Address (may be in header)

### 3. Tables
**Common in Korean resumes** and structured formats.

**Extraction method**:
```python
for table in doc.tables:
    for row in table.rows:
        cells = [cell.text for cell in row.cells]
        # Process row data
        # First cell often contains field name
        # Second cell contains value
```

**Reading order**:
- Row-by-row, left-to-right
- Handle merged cells (they appear in multiple cells with same text)
- Map field names to content (e.g., "성명" → name field)

**What to extract**:
- Personal information tables (이력서)
- Experience in tabular format
- Education history
- Skills matrices

### 4. Text Boxes and Shapes
**Often missed** by standard parsers but may contain important content.

**Extraction method**:
```python
from docx.oxml import CT_Shape

# Access XML to get shapes/text boxes
for element in doc.element.body.iter():
    if isinstance(element, CT_Shape):
        # Extract text from shape
        text_frame = element.txBody
        if text_frame:
            # Process text box content
```

**What to extract**:
- Skills summaries in side boxes
- Highlights/achievements in callout boxes
- Professional summary in header boxes

### 5. Images
**Photos** are common in Korean resumes.

**Detection method**:
```python
from docx.oxml.ns import qn

for rel in doc.part.rels.values():
    if "image" in rel.target_ref:
        # Image found - likely a photo
        image_data = rel.target_part.blob
        # Save or process image
```

**Handling**:
- Detect presence of photo
- Extract image file
- Note location for template mapping
- Resize if needed for target template

## Section Identification

### Standard Section Headings (English)

| Section Type | Common Variations |
|--------------|-------------------|
| **Experience** | Work Experience, Professional Experience, Employment History, Career History, Professional Background, Work History |
| **Education** | Academic Background, Academic History, Educational Background, Qualifications |
| **Skills** | Technical Skills, Core Competencies, Expertise, Proficiencies, Competencies, Technical Proficiencies |
| **Summary** | Professional Summary, Profile, Objective, Career Objective, About Me, Summary of Qualifications |
| **Projects** | Key Projects, Portfolio, Selected Projects |
| **Certifications** | Licenses and Certifications, Professional Certifications, Credentials |
| **Publications** | Research, Papers, Publications and Presentations |
| **Awards** | Honors and Awards, Achievements, Recognition |

### Korean Section Headings

| Section Type | Korean | Romanization |
|--------------|--------|--------------|
| **Personal Info** | 인적사항 | Injeoksahang |
| **Education** | 학력사항, 학력 | Hakryeoksahang, Hakryeok |
| **Experience** | 경력사항, 경력, 경력 개요 | Gyeongryeoksahang, Gyeongryeok |
| **Detailed Experience** | 상세경력사항 | Sangsegyeongryeoksahang |
| **Skills** | 핵심역량, 보유기술, 전문기술 | Haeksimyeokryang, Boyugisul |
| **Certifications** | 자격사항, 자격증, 면허 | Jaggyeoksahang, Jaggyeokjeung |
| **Military Service** | 병역사항 | Byeongyeoksahang |
| **Family** | 가족사항 | Gajoksahang |
| **Hobbies** | 취미, 특기 | Chwimi, Teukgi |
| **Self-Introduction** | 자기소개서 | Jagigaesoeseo |

### Section Detection Algorithm

1. **Look for explicit headings**:
   - Larger font size than body text
   - Bold or underlined
   - All caps or title case
   - Isolated on own line

2. **Match against synonym dictionary**:
   - Exact match first
   - Partial match (contains keyword)
   - Fuzzy match for typos

3. **Context-based detection**:
   - If dates in MM/YYYY or YYYY.MM format → likely Experience or Education
   - If company names detected → likely Experience
   - If school/university names → likely Education
   - If bullet points with skills/tools → likely Skills

4. **Position-based inference**:
   - Top of document → likely Summary or Contact
   - After contact info → likely Summary or Skills
   - Middle sections → likely Experience
   - Later sections → likely Education, Certifications

## Personal Information Extraction

### Name Extraction

**Strategies**:
1. **First large text** in document (often formatted larger)
2. **Header text** (frequently contains name)
3. **Field labeled** "이름", "성명", "Name"
4. **Top-left or centered** at document start

**Validation**:
- Name should be 2-4 words (Western) or 2-3 characters (Korean)
- Shouldn't contain numbers or special characters
- Should appear before other content

### Contact Information

**Phone Number Patterns**:
```
Korean: 010-XXXX-XXXX, 010.XXXX.XXXX, 010XXXXXXXX
International: +82-10-XXXX-XXXX
U.S.: (555) 123-4567, 555-123-4567
```

**Email Patterns**:
```
Standard: name@domain.com
Regex: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
```

**Address Extraction**:
- Look for street/city/state keywords
- Korean: 서울특별시, 경기도, etc.
- Often after name or in personal info section

**Portfolio/LinkedIn**:
- URLs or hyperlinked text
- Common patterns: linkedin.com/in/..., github.com/..., portfolio site
- May be in header, footer, or contact section

### Photo Handling

**Detection**: Look for images in document

**Extraction**:
- Save image bytes
- Determine dimensions
- Note position (header, top-right, etc.)

**Common Korean photo specs**:
- Size: 3x4 cm or 35x45 mm
- Position: Top right of personal info section
- Format: JPG or PNG

## Work Experience Extraction

### Experience Block Identification

**Typical structure**:
```
[Company Name] | [Job Title] | [Dates]
• Responsibility/achievement 1
• Responsibility/achievement 2
```

Or Korean table format:
```
┌──────────┬────────────────────────┐
│ 기간     │ 2020.01 ~ 2023.12      │
├──────────┼────────────────────────┤
│ 회사명   │ ABC Company            │
├──────────┼────────────────────────┤
│ 직책     │ Senior Engineer        │
├──────────┼────────────────────────┤
│ 담당업무 │ • Achievement 1        │
│          │ • Achievement 2        │
└──────────┴────────────────────────┘
```

### Company Name Detection

**Indicators**:
- Capitalized words or proper nouns
- May include Ltd, Inc, Corp, Co., 주식회사, etc.
- Often before job title
- May be hyperlinked to company website

**Validation**:
- Should not be a job title
- Often appears with other experience elements
- May have location in parentheses

### Job Title Detection

**Common patterns**:
- Engineer, Developer, Manager, Analyst, Specialist, 연구원, 팀장, etc.
- May include "Senior", "Lead", "Principal", "Junior"
- Often after company name or on same line

### Date Extraction and Normalization

**Input formats**:
```
Korean:
- 2023년 7월 ~ 현재
- 2023.07 ~ 재직중
- 2023/07 - Present

Western:
- July 2023 - Present
- 07/2023 - Current
- 2023-07 to Now
```

**Normalization strategy**:
1. **Extract** using regex patterns
2. **Parse** month and year
3. **Convert** to standard format (YYYY.MM or YYYY-MM)
4. **Handle** "Present", "현재", "재직중" → current date or "Present"

**Date regex patterns**:
```python
# Korean
r'\d{4}년\s*\d{1,2}월'
r'\d{4}\.\d{2}'

# Western
r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
r'\d{1,2}/\d{4}'
```

### Responsibilities and Achievements

**Extraction**:
- Bullet points (•, -, *, numbers)
- Paragraphs under job title
- Table cells labeled "담당업무", "주요업무", "Responsibilities"

**Key elements to preserve**:
- Quantified metrics (increased by 40%, saved $100K, etc.)
- Technical tools and frameworks (PyTorch, AWS, React)
- Scale indicators (managed team of 5, processed 1M records)
- Action verbs (Developed, Led, Architected)

## Education Extraction

### University/School Name

**Indicators**:
- Contains "University", "College", "Institute", "대학교", "대학"
- Proper noun, capitalized
- May include location

**Validation**:
- Appears in education section
- Associated with degree and dates
- Well-known institution names

### Degree Extraction

**Common degrees**:
- Bachelor of Science (BS, B.S., B.Sc.)
- Master of Science (MS, M.S., M.Sc.)
- PhD, Doctorate
- 학사, 석사, 박사 (Korean)

**Associated fields**:
- Computer Science, Engineering, Business, etc.
- May be in parentheses or on same line

### GPA Extraction

**Patterns**:
```
- 3.8/4.0
- GPA: 3.8
- 4.23/4.5
- (3.5/4.5)
```

**Validation**:
- Number between 0-5
- Often has denominator (out of 4.0, 4.3, 4.5)
- Near degree information

### Dates

Similar to experience dates. Often just year:
```
- 2015 - 2019
- 2015.03 ~ 2019.02
- Graduated May 2019
```

## Skills Extraction

### Technical Skills

**Identification**:
- Section labeled Skills, Technologies, Technical Skills, 보유기술
- Comma-separated lists
- Bullet points
- Tables with proficiency levels

**Common categories**:
- Programming Languages: Python, Java, JavaScript, C++
- Frameworks: React, Django, TensorFlow, PyTorch
- Tools: Git, Docker, AWS, Jenkins
- Databases: MySQL, PostgreSQL, MongoDB

**Proficiency levels**:
- Expert, Advanced, Intermediate, Beginner
- Years of experience (5+ years, 2 years)
- 상급, 중급, 초급 (Korean)

### Language Skills

**Languages**:
- English, Korean (한국어), Japanese (일본어), Chinese (중국어)
- May include proficiency: Native, Fluent, Conversational, Basic
- Certifications: TOEIC 900, TOPIK Level 6

### Certifications

**Format**:
- Certification name + issuing organization + date
- AWS Certified Solutions Architect (Amazon, 2023)
- PMP Certification (PMI)

## Multi-Column Layout Handling

### Reading Order Detection

**Strategy 1: Position-based**
```
Analyze x-coordinates:
- If x < page_width/2 → Left column
- If x >= page_width/2 → Right column

Sort by:
1. Column (left first)
2. Y-position (top to bottom)
```

**Strategy 2: Visual gap detection**
```
Identify large horizontal gaps in text:
- Gap > threshold → column boundary
- Read top-to-bottom in each column
```

### Common Layouts

**Sidebar + Main** (most common):
```
┌─────────┬──────────────────┐
│ Sidebar │   Main Content   │
│(25-30%) │    (70-75%)      │
├─────────┼──────────────────┤
│ Contact │   Summary        │
│ Skills  │   Experience     │
│ Langs   │   Education      │
└─────────┴──────────────────┘

Read: Sidebar completely, then Main
```

**Two equal columns**:
```
┌────────────────┬────────────────┐
│  Left (50%)    │  Right (50%)   │
├────────────────┼────────────────┤
│  Experience 1  │  Experience 2  │
│  Education     │  Skills        │
└────────────────┴────────────────┘

Read: Top-to-bottom left, then right
OR: Row-by-row if content is related
```

## Korean-Specific Elements

### Age and Birth Date

**Formats**:
- 생년월일: 1990년 1월 1일 (만 34세)
- Born: 1990.01.01
- Age: 34 (or 35 in Korean age)

**Important**:
- Korean age (한국 나이) = Current year - Birth year + 1
- International age = Current year - Birth year (if birthday passed)
- Clarify which system is used

### Military Service (병역사항)

**Common for Korean men**:
- 군필 (Completed)
- 면제 (Exempted)
- 미필 (Not completed)
- Service branch: 육군 (Army), 해군 (Navy), 공군 (Air Force)
- Dates: 2010.03 ~ 2012.01

### Family Information (가족사항)

**Sometimes included** (less common in modern resumes):
- 부 (Father), 모 (Mother), 배우자 (Spouse)
- Names, ages, occupations
- Note: May be considered outdated/unnecessary

### Hobbies (취미/특기)

**Often included** to show personality:
- Sports, reading, music, etc.
- May be in personal info section
- Usually brief (1-2 items)

## Missing Sections Handling

### Graceful Degradation

When standard sections are missing:

**No Experience Section**:
- Look for Projects section instead
- Check for internships or volunteer work
- Flag in output that full-time experience not found

**No Education Section**:
- May be entry-level without degree
- Look for certifications or training
- Flag if truly absent

**No Skills Section**:
- Extract skills mentioned in experience descriptions
- Infer from job titles and responsibilities
- Create derived skills list

**No Contact Info**:
- CRITICAL - must find or ask user
- Check all document locations thoroughly
- Flag as high-priority missing info

## Confidence Scoring

Assign confidence to each extracted field:

**High Confidence (0.8 - 1.0)**:
- Found in expected location
- Clear field label
- Standard format
- Validated against patterns

**Medium Confidence (0.5 - 0.79)**:
- Found but location unusual
- Inferred from context
- Format slightly non-standard
- Partial match to patterns

**Low Confidence (0.0 - 0.49)**:
- Ambiguous location
- No clear label
- Multiple possible interpretations
- Failed validation checks

**Use confidence scores** to:
- Flag fields for manual review
- Prioritize in validation report
- Decide whether to use or skip content

## Example Extraction Output

```json
{
  "personal_info": {
    "name": {"value": "문다빈", "confidence": 0.95, "source": "header"},
    "phone": {"value": "010-9860-8431", "confidence": 1.0, "source": "header"},
    "email": {"value": "dabs.damoon@gmail.com", "confidence": 1.0, "source": "header"},
    "address": {"value": "서울특별시 서초구", "confidence": 0.8, "source": "body"},
    "photo": {"present": false, "confidence": 1.0}
  },
  "experience": [
    {
      "company": {"value": "Hudson AI", "confidence": 0.9},
      "title": {"value": "AI Researcher/Engineer", "confidence": 0.9},
      "start_date": {"value": "2023.07", "confidence": 1.0},
      "end_date": {"value": "Present", "confidence": 1.0},
      "responsibilities": [
        {"value": "음성합성 알고리즘 개선 연구", "confidence": 0.85},
        {"value": "TTS 모델 학습 및 추론 파이프라인 구축", "confidence": 0.85}
      ]
    }
  ],
  "skills": {
    "technical": [
      {"value": "PyTorch", "confidence": 0.95, "category": "ML Framework"},
      {"value": "TensorFlow", "confidence": 0.95, "category": "ML Framework"}
    ],
    "languages": [
      {"value": "Korean", "confidence": 1.0, "proficiency": "Native"},
      {"value": "English", "confidence": 0.9, "proficiency": "Professional"}
    ]
  },
  "education": [],
  "metadata": {
    "source_file": "resume.docx",
    "extraction_date": "2025-01-15",
    "overall_confidence": 0.88,
    "layout_type": "free-form",
    "warnings": ["No education section found"]
  }
}
```
