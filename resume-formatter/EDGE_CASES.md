# Resume Formatter - Edge Cases & Robustness

## Edge Cases Handled

This document catalogs the various edge cases and challenging resume formats that the resume-formatter skill is designed to handle.

## 1. Layout Complexity

### Multi-Column Layouts
```
┌─────────────────────────────────────┐
│  SIDEBAR    │   MAIN CONTENT        │
│  (Column 1) │   (Column 2)          │
├─────────────┼───────────────────────┤
│  Photo      │   Name                │
│  Contact    │   Summary             │
│  Skills     │                       │
│  - Python   │   Experience          │
│  - Java     │   - Job 1             │
│  Languages  │   - Job 2             │
│  - Korean   │                       │
│  - English  │   Education           │
└─────────────┴───────────────────────┘

Reading Order Challenge:
- Must read sidebar completely, then main content
- Or interleave based on visual position
- Skill uses position analysis (x, y coords)
```

### Three-Column Layout
```
┌────────────────────────────────────────────┐
│  LEFT      │  CENTER      │  RIGHT         │
├────────────┼──────────────┼────────────────┤
│  Contact   │  Name        │  Photo         │
│  Skills    │  Summary     │  QR Code       │
│            │  Experience  │  Languages     │
│            │  Education   │  Certifications│
└────────────┴──────────────┴────────────────┘
```

### Table-Based Resume
```
┌───────────────────────────────────────────┐
│ 인적사항                                   │
├──────────┬────────────────────────────────┤
│ 성명     │ 문다빈                         │
├──────────┼────────────────────────────────┤
│ 생년월일 │ 1990.01.01 (만 34세)           │
├──────────┼────────────────────────────────┤
│ 연락처   │ 010-1234-5678                  │
│          │ email@example.com              │
└──────────┴────────────────────────────────┘

Challenge: Extract cell-by-cell while maintaining relationships
```

## 2. Content Location Edge Cases

### Critical Info in Header
```
┌─────────────────────────────────────────┐
│ [HEADER]                                │
│ John Smith | 010-1234-5678 | email.com  │ ← Important!
├─────────────────────────────────────────┤
│ [MAIN BODY]                             │
│ Experience...                           │
│ ...                                     │
└─────────────────────────────────────────┘

Risk: ATS/parsers often ignore headers
Solution: Multi-pass extraction checks headers first
```

### Text Boxes
```
┌─────────────────────────────────────────┐
│ ╔══════════════════╗                    │
│ ║  SKILLS SUMMARY  ║ ← Text Box         │
│ ║  - Python        ║   (often ignored)  │
│ ║  - Machine Learning ║                 │
│ ╚══════════════════╝                    │
│                                         │
│ Work Experience...                      │
└─────────────────────────────────────────┘

Risk: python-docx doesn't extract text boxes by default
Solution: Access document.element and extract shapes
```

### Footer Page Numbers and Metadata
```
┌─────────────────────────────────────────┐
│ [MAIN CONTENT]                          │
│ ...                                     │
├─────────────────────────────────────────┤
│ [FOOTER]                                │
│ Last updated: 2025-01-15 | Page 1 of 2  │
│ Portfolio: www.example.com              │ ← Links!
└─────────────────────────────────────────┘

Extract: Portfolio links, last update dates
```

## 3. Non-Standard Section Headings

### Synonyms for Common Sections

| Standard | Variations |
|----------|-----------|
| Experience | 경력사항, Work History, Professional Background, Career Synopsis, Employment History |
| Education | 학력사항, Academic Background, Qualifications, Educational History |
| Skills | 핵심역량, Technical Skills, Core Competencies, Expertise, Proficiencies |
| Summary | 자기소개, Objective, Profile, Professional Summary, About Me |

**Solution**: Maintain synonym mapping dictionary + use LLM for semantic understanding

## 4. Date Format Variations

### Multiple Date Formats
```
Korean:
- 2023년 7월 ~ 현재
- 2023.07 ~ 재직중
- 2023/07 - Present

Western:
- July 2023 - Present
- 07/2023 - Current
- 2023-07 to Now

Mixed:
- 2023.07.15 ~ 2024년 1월
```

**Solution**: Date format normalization with regex patterns

## 5. Content Structure Variations

### Experience Section Formats

**Bullet Points (Western):**
```
Software Engineer | ABC Company | 2020-2023
• Developed ML models achieving 95% accuracy
• Led team of 5 engineers
• Reduced latency by 40%
```

**Paragraph (Creative):**
```
As a Software Engineer at ABC Company (2020-2023), I developed
machine learning models that achieved 95% accuracy while leading
a team of 5 engineers and reducing system latency by 40%.
```

**Table (Korean Standard):**
```
┌──────────┬────────────────────────────────────┐
│ 기간     │ 2020.01 ~ 2023.12                  │
├──────────┼────────────────────────────────────┤
│ 회사명   │ ABC 컴퍼니                         │
├──────────┼────────────────────────────────────┤
│ 직책     │ 소프트웨어 엔지니어                 │
├──────────┼────────────────────────────────────┤
│ 담당업무 │ • ML 모델 개발 (정확도 95% 달성)   │
│          │ • 5명 팀 리드                       │
│          │ • 시스템 레이턴시 40% 감소          │
└──────────┴────────────────────────────────────┘
```

## 6. Missing or Incomplete Sections

### Examples:
- **Entry-level resume**: No experience section (only education + projects)
- **Career changer**: No relevant experience in target field
- **Freelancer**: Multiple short-term gigs instead of traditional employment
- **Academic**: Heavy on publications, light on work experience
- **Creative**: Portfolio links but minimal formal experience

**Solution**: Graceful degradation - work with what's available, flag missing sections

## 7. Overflow Content

### Long Experience Section
```
Template allows: 3-4 bullet points per job
Candidate has: 15 bullet points for current role

Options:
1. Truncate (risky - lose information)
2. Summarize intelligently (preserve key achievements)
3. Ask user which to prioritize
4. Use multiple pages if template allows
```

**Solution**: Implement intelligent summarization with priority ranking

## 8. Korean-Specific Edge Cases

### 인적사항 (Personal Information) Variations
```
Standard fields:
- 성명 (Name)
- 생년월일/나이 (Birth date/Age)
- 성별 (Gender)
- 주소 (Address)
- 연락처 (Contact)

Sometimes included:
- 사진 (Photo)
- 병역사항 (Military service - male only)
- 가족사항 (Family details - sometimes considered outdated)
- 취미 (Hobbies)
- 특기 (Special skills)
```

### Age Calculation Edge Case
```
Korean Age (한국 나이):
- Born 1990.12.30
- On 2025.01.01 → Korean age = 36
- International age = 34

Must clarify which age system to use!
```

## 9. File Format Issues

### .doc vs .docx
```
.doc (Word 97-2003):
- Binary format
- Requires different parsing library
- May have encoding issues with Korean text

.docx (Word 2007+):
- XML-based format
- Better support with python-docx
- Generally more reliable
```

### Encoding Issues
```
Korean text encodings:
- UTF-8 (modern, preferred)
- EUC-KR (older Korean standard)
- CP949 (Windows Korean)

Issue: Garbled text if wrong encoding detected
Solution: Try multiple encodings, use chardet library
```

## 10. Visual Elements

### Photos
```
Korean resumes often include:
┌────────┐
│ Photo  │  3x4 cm or 35x45 mm
│        │  Professional headshot
└────────┘

Challenges:
- Extract photo from source
- Resize to template requirements
- Position correctly in target template
- Handle missing photos gracefully
```

### QR Codes & Graphics
```
Modern resumes may include:
- QR code linking to portfolio
- Skill proficiency bars/charts
- Timeline graphics
- Company logos

Challenge: Extract as images or ignore?
Solution: Preserve if template supports, otherwise extract linked URL
```

## 11. Multi-Page Resumes

```
Page 1: Personal info, summary, key skills
Page 2: Detailed work experience
Page 3: Projects, publications, certifications

Challenges:
- Header/footer may differ per page
- Content flow across pages
- Template might be single-page only

Solution:
- Extract all pages
- Consolidate content
- Intelligently summarize if target is single-page
```

## Accuracy Targets by Complexity

| Resume Type | Complexity | Target Accuracy |
|------------|-----------|----------------|
| Simple chronological, single-column | Low | 94-96% |
| Standard Korean table format | Low | 94-96% |
| Two-column layout | Medium | 88-92% |
| Three-column layout | Medium-High | 85-90% |
| Headers/footers with key info | Medium | 85-91% |
| Text boxes and shapes | High | 75-85% |
| Creative/infographic style | Very High | 70-82% |
| Scanned/image-based | Very High | 70-80% |

## Testing Strategy

For each edge case category:
1. Create 2-3 test resume examples
2. Define expected extraction output
3. Run parser and compare results
4. Calculate accuracy percentage
5. Iterate until meeting target accuracy
6. Document any persistent limitations

## Fallback Strategies

When parsing fails:
1. **Partial extraction**: Return what was successfully extracted
2. **Confidence scores**: Flag low-confidence fields
3. **Manual review prompts**: Ask user to verify/correct specific fields
4. **Alternative extraction**: Try different parsing strategies
5. **Graceful failure**: Never crash - always return *something*
