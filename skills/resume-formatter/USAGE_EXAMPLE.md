# Resume Formatter - Usage Example

## Example Session

### User Request
```
I'm a headhunter and need to reformat this candidate's resume to our client's
Meta Search template. The candidate is 문다빈 (Dabin Moon).

[Attaches two files:]
- Source: 이력서_v2025-10-26_sub_v1.0.docx (candidate's personal format)
- Template: 메타써치_국문이력서_샘플.docx (Meta Search standard format)
```

### Claude's Response

**Step 1: Understanding**
```
I'll reformat 문다빈's resume to the Meta Search template format. Let me:
1. Extract content from the source resume
2. Map it to the Meta Search template structure
3. Validate completeness

Starting extraction...
```

**Step 2: Extraction**
```
Running: python scripts/resume_parser.py "이력서_v2025-10-26_sub_v1.0.docx"

Extracted:
✓ Name: 문다빈
✓ Contact: 010-9860-8431, dabs.damoon@gmail.com
✓ Address: 서울특별시 서초구
✓ Experience: 1 entry (Hudson AI, AI Researcher/Engineer, 2023.07-현재)
✓ Skills: ML/DL Frameworks, Audio Processing, MLOps, LLM/Agents
⚠ Education: Found but needs verification
⚠ Birth year/gender: Not found in source

Confidence: 85%
```

**Step 3: Mapping**
```
Mapping to Meta Search template structure...

Template sections:
- 지원분야 (Application Field)
- 인적사항 (Personal Information)
- 학력사항 (Education)
- 핵심역량 (Core Competencies)
- 경력사항 (Career Summary)
- 상세경력사항 (Detailed Experience)

Mapping completed with intelligent summarization.
```

**Step 4: Validation**
```
Validation Results:

Overall Completeness: 92%

Section Breakdown:
✓ Personal Info: 100%
✓ Core Competencies: 95%
✓ Experience: 100%
⚠ Education: 85% (some details unclear)
⚠ Birth/Gender: Missing from source

Issues Found:
⚠ 생년/성별 field: Information not available in source resume
⚠ 학력사항: GPA not found

All critical information preserved:
✓ Name, contact info
✓ Work experience with achievements
✓ Technical skills
✓ Quantified metrics (40% latency reduction, 50+ languages, etc.)
```

**Step 5: Delivery**
```
Created: 문다빈_MetaSearch_formatted.docx

Summary of transformations:
- Extracted personal info from source
- Mapped 1.5 years of AI/ML experience to 상세경력사항
- Consolidated technical skills into 핵심역량 (top 5 competencies)
- Preserved all quantified achievements (40% latency, MOS/PESQ metrics)
- Formatted dates to Meta Search convention (YYYY.MM)
- Marked missing fields: 생년/성별 as "정보 없음"

Please review:
1. Birth year/gender: Source resume doesn't include this. Should I ask the
   candidate or leave as "정보 없음"?
2. Education GPA: Not found in source. Acceptable to omit?
3. Military service (병역사항): Not in template, but often required. Add section?

[Provides formatted resume file for download]
```

### User Feedback
```
Looks good! Please:
1. Leave birth/gender as "정보 없음" - we'll get that from candidate later
2. GPA is fine to omit
3. No need for military service section in this template

One more thing: can you make the 핵심역량 section more specific about the
AI/ML experience?
```

### Claude's Adjustment
```
Updated 핵심역량 section with more specific details:

Before:
• ML/DL Frameworks (PyTorch, TensorFlow) 경험
• AWS/GCP MLOps 파이프라인 구축 경험

After:
• 다국어 TTS 모델 개발 및 최적화 전문성 (PyTorch, TensorFlow 활용)
• AWS/GCP 기반 ML 파이프라인 구축 및 운영 (latency 40% 개선 실적)
• LLM/RAG 시스템 설계 및 구현 경험 (LangChain, Claude/Gemini/GPT)

Updated file: 문다빈_MetaSearch_formatted_v2.docx

All set! The resume is now formatted to Meta Search standards while preserving
all technical achievements and quantified metrics.
```

## Command-Line Usage (Advanced)

For power users, the scripts can be run directly:

### Extract Content
```bash
cd /Users/dabsdamoon/projects/anthropic-skills/resume-formatter

python scripts/resume_parser.py \
  "tests/format_before/이력서_v2025-10-26_sub_v1.0.docx" \
  --output extracted.json
```

**Output:**
```json
{
  "personal_info": {
    "name": {"value": "문다빈", "confidence": 0.95},
    "phone": {"value": "010-9860-8431", "confidence": 1.0},
    "email": {"value": "dabs.damoon@gmail.com", "confidence": 1.0}
  },
  "experience": [...],
  "skills": {...},
  "metadata": {
    "overall_confidence": 0.85,
    "warnings": [...]
  }
}
```

### Map to Template
```bash
python scripts/template_mapper.py \
  extracted.json \
  "tests/format_to/메타써치_국문이력서_샘플.docx" \
  --output mapped_resume.docx
```

### Validate Result
```bash
python scripts/content_validator.py \
  extracted.json \
  mapped_resume.docx
```

**Output:**
```
VALIDATION REPORT
============================================================

Overall Completeness: 92.0%

Section Completeness:
  ✓ personal_info: 100.0%
  ✓ experience: 100.0%
  ✓ skills: 90.0%
  ⚠ education: 80.0%

Issues Found (2):
  ⚠ Personal info 'birth_year' not found in target
  ⚠ Education GPA not specified

Recommendations:
  - Review flagged missing content above
  - Verify critical fields (name, contact) are correct
```

## Tips for Best Results

### 1. Provide Clear Context
```
Good: "Convert this resume to Meta Search format for a senior AI engineer position"
Better: "Reformat to Meta Search template, emphasizing ML achievements from last 2 years"
```

### 2. Specify Missing Information
```
"The candidate doesn't have a photo - leave that blank"
"Birth year is 1990, please add that to 생년/성별"
"Prioritize recent experience, older roles can be summarized"
```

### 3. Review Critical Fields
Always verify:
- ✓ Name spelling
- ✓ Contact information
- ✓ Dates (start/end for each role)
- ✓ Recent achievements and metrics

### 4. Provide Feedback
If something doesn't look right:
```
"The experience section looks too brief - can you expand the most recent role?"
"The skills list is too long - keep only top 8"
"Some achievements are missing - please check the source resume for quantified results"
```

## Common Scenarios

### Scenario 1: Headhunter with Multiple Candidates
```
"I have 5 candidate resumes that all need to be reformatted to the same
client template. Let's do them one by one."

[Provides source resume #1 and template]
[Reviews and approves]
[Repeats for candidates 2-5]
```

### Scenario 2: Applicant with Multiple Target Companies
```
"I need my resume in 3 different formats:
1. Meta Search template
2. J&J template
3. Standard Western chronological format

Let's start with Meta Search."

[Provides source resume and each template]
```

### Scenario 3: Incomplete Source Resume
```
"This candidate's resume is missing their education section and I know they
have a Master's degree from Seoul National University (2020). Please add that."

[Claude extracts what's available, asks for missing info, and fills in provided details]
```

## Troubleshooting

### Issue: Low Confidence Score
**Cause:** Source resume has unusual format or missing sections

**Solution:**
- Provide additional context about the source
- Manually specify critical missing information
- Review extraction results and correct as needed

### Issue: Content Overflow
**Cause:** Source has more content than template can fit

**Solution:**
- Ask Claude to prioritize recent experience
- Specify which roles to emphasize
- Accept intelligent summarization for older roles

### Issue: Formatting Looks Wrong
**Cause:** Template structure different from expected

**Solution:**
- Verify you're using the correct template file
- Check if template has unusual structure (Claude will adapt)
- Provide example of desired output format

## Next Steps

After receiving the reformatted resume:
1. ✅ Download the file
2. ✅ Open in Word to verify formatting
3. ✅ Check all critical information
4. ✅ Make any manual adjustments needed
5. ✅ Send to candidate/client for final review

The skill aims for 90%+ accuracy, but human review is always recommended for
professional documents!
