# Resume Formatter Skill - Evaluation Report

## Test Case Details

**Source Resume:** `이력서_v2025-10-26_sub_v1.0.docx` (문다빈)
**Target Template:** `이력서 양식(엔지니어)_송부.docx`
**Result:** `문다빈_이력서_엔지니어양식_최종본.docx`
**Date:** 2025-11-16

## Overall Assessment

**Success Rate: 60%** ⚠️

The skill successfully extracted and mapped most content, but has several critical issues that need addressing.

---

## ✅ What Worked Well

### 1. Personal Information Mapping (95% Success)
**Excellent performance**:
- ✓ Name correctly mapped: 문다빈 (Dabin Moon)
- ✓ Contact info accurate: (+82) 10-9860-8431, dabs.damoon@gmail.com
- ✓ Address preserved: 서울특별시 서초구 동광로
- ✓ Handled missing fields gracefully:
  - 생년월일: "정보 없음" (appropriate placeholder)
  - 현재연봉/희망연봉: "협의 가능" (reasonable default)
  - 입사시기: "협의 가능"
- ✓ Gender inferred: 남 / 미혼

**Minor issue**:
- Gender/marital status was inferred (not in source) - should be marked as "정보 없음" or confirmed with user

### 2. Education Mapping (100% Success)
**Perfect execution**:
```
✓ 2014.09~2015.12  Columbia University 통계학 석사 졸업 (New York, NY, 3.4/4.0)
✓ 2009.09~2013.05  Boston College 수학/경제학 복수전공, 음악 부전공 학사 졸업 (Chestnut Hill, MA, 3.6/4.0)
```

- Dates correctly formatted
- School names preserved
- Majors/minors included
- GPAs accurate
- Locations included

### 3. Core Competencies (핵심역량) (90% Success)
**Good summarization**:
```
✓ 음성합성 및 대화형 AI 분야에서 7년 이상 연구/개발 경험 (TTS, Auto-Dubbing, LLM 기반 대화 엔진)
✓ PyTorch, TensorFlow 기반 ML/DL 모델 개발부터 AWS/GCP 기반 MLOps 파이프라인 구축
✓ TTS 프로덕트(Timbr, AUDIC) 및 대화형 AI 서비스(PULSE) 개발 리딩 및 상용화 경험
```

- Captured domain expertise (TTS, Audio AI)
- Mentioned key products (Timbr, AUDIC, PULSE)
- Highlighted technical stack
- Good level of detail

**Issue**: "7년 이상" may be inaccurate - actual experience appears to be ~7 years from 2018-2025, but skill calculated it

### 4. Technical Skills (기술스택) (85% Success)
**Well organized**:
```
✓ Python, SQL
✓ Cloud: AWS, GCP
✓ ML/DL: PyTorch, TensorFlow, Scikit-learn
✓ MLOps: Git, Docker
✓ LLM/Agents: LangChain, Claude Code, Gemini Cli, RAG
✓ Audio Processing: librosa, torchaudio, nnAudio, soundfile
```

- Properly categorized
- Preserved specific tool names
- Good breadth of coverage

**Issues**:
- Missing some tools from source (e.g., Kubernetes, Airflow mentioned in template but could be added if relevant)
- Could be more comprehensive

---

## ❌ Critical Issues Found

### 1. **LinkedIn URL Duplication Bug** (CRITICAL)
**Problem**: LinkedIn URL repeated 25+ times in a row
```
❌ LinkedIn: https://www.linkedin.com/in/dabin-moon-b4042378/
❌ LinkedIn: https://www.linkedin.com/in/dabin-moon-b4042378/
❌ LinkedIn: https://www.linkedin.com/in/dabin-moon-b4042378/
[... 22 more times ...]
```

**Root Cause**: Likely a bug in template mapping logic where the portfolio/LinkedIn field got stuck in a loop.

**Impact**: Severe - makes document look unprofessional and broken

**Fix Priority**: 🔴 **CRITICAL - Must fix immediately**

**Recommended Fix**:
```python
# In template_mapper.py, add deduplication check
def _add_to_document(self, text, max_consecutive_duplicates=2):
    """Prevent duplicate lines from being added"""
    if hasattr(self, '_last_added_lines'):
        if text in self._last_added_lines[-3:]:  # Check last 3 lines
            return  # Skip duplicate
    # Add text to document
```

### 2. **Missing Detailed Experience Section** (CRITICAL)
**Problem**: The most important section - detailed work experience - was NOT filled in from source resume

**What should have been mapped**:

From source (Hudson AI, 2023.07-현재):
```
✗ 음성합성 알고리즘 개선 연구
✗ 다국어 TTS 모델 학습 및 추론 파이프라인 구축
✗ TTS 전/후처리 알고리즘 연구
✗ vocoder from-scratch 및 fine-tuning (BigVGAN, RingFormer)
✗ PULSE 대화 엔진 구축
✗ Auto-Dubbing 파이프라인 구축
```

From source (KRAFTON, 2022.09-2023.07):
```
✗ AUDIC 프로덕트 TTS 퀄리티 개선 연구
✗ 개인화 TTS 연구
✗ 화자디자인 기능 추가
```

**What actually appeared**: Template placeholder text only
```
❌ 2000.00~ 재직 중    회사이름 / 부서명 / 직무 / 직급(직책)
❌ [회사소개] - 업종 및 제품 : ㅇㅇ제조 및 유통 회사
❌ [담당 업무] 1. Lead ML 2. 000 3. ㅇㅇㅇ
❌ [주요 업무/성과] 1. LLM/생성형 AI ... (template example text)
```

**Impact**: Severe - the entire work history is missing!

**Fix Priority**: 🔴 **CRITICAL - Core functionality failure**

**Root Cause**:
1. Parser may have extracted experience but mapper didn't populate the detailed section
2. Template structure not recognized properly
3. Field mapping logic failed to match "경력 세부사항" with extracted experience

**Recommended Fix**:
```python
# In template_mapper.py
def _map_detailed_experience(self):
    """Map detailed experience to 경력 세부사항 section"""
    # Find the section in template
    for para_idx, para in enumerate(self.doc.paragraphs):
        if '경력 세부사항' in para.text or '세부사항' in para.text:
            # Found section - now populate with actual experience
            insert_point = para_idx + 1

            for exp in self.data.get('experience', []):
                # Create job entry
                self._insert_job_block(insert_point, exp)
                insert_point += len(job_block_lines)

            # Remove template placeholder text
            self._remove_template_placeholders(para_idx, para_idx + 30)
```

### 3. **경력사항 Summary Not Updated** (HIGH Priority)
**Problem**: Brief career summary shows template placeholders instead of actual companies:

```
❌ 2021.02~재직 중	회사이름 / 부서명 / 직무 / 직급(직책)
❌ 2016.01~2021.02	회사이름 / 부서명 / 직무 / 직급(직책)
```

**Should be**:
```
✓ 2023.07~재직 중	Hudson AI / AI Research / AI Researcher/Engineer
✓ 2022.09~2023.07	KRAFTON, Beluga Part / ML 엔지니어
✓ 2018.04~2022.09	Lablup Inc. / 소프트웨어 엔지니어
```

**Fix Priority**: 🔴 **HIGH - Core information missing**

### 4. **Total Experience Duration Not Calculated**
**Problem**: Shows "총 경력 : 00년 00개월" instead of calculating actual duration

**Should be**: "총 경력 : 7년 4개월" (2018.04 ~ 2025.11 with gaps considered)

**Fix Priority**: 🟡 **MEDIUM - Nice to have**

**Recommended Fix**:
```python
def calculate_total_experience(experience_list):
    """Calculate total years and months of experience"""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    total_months = 0
    for exp in experience_list:
        start = parse_date(exp['start_date'])
        end = parse_date(exp['end_date']) if exp['end_date'] != 'Present' else datetime.now()
        delta = relativedelta(end, start)
        total_months += delta.years * 12 + delta.months

    years = total_months // 12
    months = total_months % 12
    return f"{years}년 {months}개월"
```

### 5. **Template Placeholder Text Not Removed**
**Problem**: Several template example sections remain:

```
❌ [회사소개] - 업종 및 제품 : ㅇㅇ제조 및 유통 회사
❌ [담당 업무] 1. Lead ML 2. 000 3. ㅇㅇㅇ
❌ 병  역 : 육군 만기제대 (2000.00~2000.00)
❌ 어  학 : Business 회화 / OPIC Level : IH (2000.00.00)
❌ 자격증 : 빅데이터 분석기사 (2021. 한국데이터산업진흥원)
```

**Impact**: Confusing - looks like resume contains fake information

**Fix Priority**: 🔴 **HIGH - Unprofessional appearance**

**Recommended Fix**: Clear all template placeholders that weren't filled with actual data

---

## 🟡 Medium Priority Issues

### 6. Missing Information Handling

**Fields that should be marked "정보 없음"** but show template text:
- 병역 (Military service)
- 어학 (Language proficiency)
- 자격증 (Certifications)
- 자기소개 (Self-introduction)

**Current behavior**: Leaves template example text

**Better approach**: Either:
1. Mark as "정보 없음" or "해당 없음"
2. Remove section entirely if no data
3. Ask user if they want to provide this information

### 7. Work Experience Gaps

**Source has 3+ roles**:
1. Hudson AI (2023.07 - 현재)
2. KRAFTON (2022.09 - 2023.07)
3. Lablup Inc. (2018.04 - 2022.09) - not even mentioned!
4. Possibly more...

**Result mapped**: 0 roles in detail section

### 8. Portfolio/LinkedIn Placement

LinkedIn should appear once in a logical place (probably under 포트폴리오 in 기술스택 or in contact info), not 25 times.

---

## 📊 Detailed Scoring

| Category | Score | Status | Notes |
|----------|-------|--------|-------|
| **Personal Info** | 95% | ✅ Good | Minor: gender inferred not confirmed |
| **Education** | 100% | ✅ Perfect | Excellent formatting and accuracy |
| **Core Competencies** | 90% | ✅ Good | Well summarized, minor accuracy on "7년" |
| **Technical Skills** | 85% | ✅ Good | Well organized, could be more comprehensive |
| **경력사항 Summary** | 0% | ❌ Failed | Shows template placeholders |
| **경력 세부사항** | 0% | ❌ Failed | No actual work history filled in |
| **LinkedIn/Portfolio** | 0% | ❌ Failed | Duplicated 25+ times (critical bug) |
| **Template Cleanup** | 30% | ❌ Poor | Many placeholders remain |
| **Overall Quality** | 60% | ⚠️ Needs Work | Core sections missing |

---

## 🔧 Recommended Improvements to Skill

### Priority 1: Fix Critical Bugs (Blocker)

**1.1 Fix LinkedIn Duplication**
```python
# File: scripts/template_mapper.py
# Add to _map_paragraphs() or wherever portfolio is handled

class TemplateMapper:
    def __init__(self):
        self.added_links = set()  # Track added URLs

    def _add_portfolio_link(self, url):
        # Prevent duplicate links
        if url in self.added_links:
            return
        self.added_links.add(url)
        # Add to document once
```

**1.2 Implement Detailed Experience Mapping**
```python
# File: scripts/template_mapper.py

def _map_detailed_experience_section(self):
    """Map source experience to template's 경력 세부사항 section"""

    # Find section start
    detail_section_idx = self._find_section('경력 세부사항')
    if detail_section_idx is None:
        self.warnings.append("경력 세부사항 section not found in template")
        return

    # Remove template placeholder content
    self._remove_template_content(detail_section_idx + 1, detail_section_idx + 30)

    # Insert actual experience entries
    insert_idx = detail_section_idx + 1
    for exp in self.data.get('experience', []):
        job_block = self._format_job_detail(exp)
        self._insert_paragraphs(insert_idx, job_block)
        insert_idx += len(job_block)

def _format_job_detail(self, exp):
    """Format a job entry for detailed section"""
    lines = []

    # Header: dates and company info
    dates = f"{exp.get('start_date', '')}~ {exp.get('end_date', '재직 중')}"
    company = exp.get('company', '회사명')
    title = exp.get('title', '직무')
    lines.append(f"{dates}    {company} / {title}")

    # Company intro if available
    if exp.get('company_description'):
        lines.append("[회사소개]")
        lines.append(f"- {exp['company_description']}")

    # Responsibilities
    if exp.get('responsibilities'):
        lines.append("[주요 업무/성과]")
        for i, resp in enumerate(exp['responsibilities'], 1):
            lines.append(f"{i}. {resp}")

    lines.append("")  # Blank line separator
    return lines
```

**1.3 Map Career Summary (경력사항)**
```python
def _map_career_summary(self):
    """Fill in 경력사항 with brief company/date list"""
    summary_idx = self._find_section('경력사항')

    # Remove placeholder lines
    self._remove_template_placeholders(summary_idx + 1, summary_idx + 5)

    # Add actual career entries
    insert_idx = summary_idx + 1
    for exp in self.data.get('experience', []):
        dates = f"{exp.get('start_date', '')}~{exp.get('end_date', '재직중')}"
        company = exp.get('company', '')
        title = exp.get('title', '')
        line = f"{dates}\t{company} / {title}"
        self._insert_paragraph(insert_idx, line)
        insert_idx += 1
```

### Priority 2: Improve Template Cleanup

**2.1 Detect and Remove Unfilled Placeholders**
```python
def _cleanup_template_placeholders(self):
    """Remove placeholder text that wasn't filled with actual data"""
    placeholders = [
        '회사이름', '부서명', '직무', '직급(직책)',
        'ㅇㅇ제조', 'ㅇㅇㅇ',
        '0,000억원', '0,000만원',
        '2000.00', '00년 00개월',
        'Business 회화',
        '[자유양식]'
    ]

    for para in self.doc.paragraphs:
        for placeholder in placeholders:
            if placeholder in para.text:
                # Either clear it or mark as 정보 없음
                if self._is_required_field(para.text):
                    # Mark missing
                    para.text = para.text.replace(placeholder, '정보 없음')
                else:
                    # Remove optional field
                    para.text = ""
```

**2.2 Handle Missing Fields Consistently**
```python
def _handle_missing_fields(self):
    """Consistent handling of fields with no source data"""

    missing_fields = {
        '병역': self.data.get('military_service'),
        '어학': self.data.get('language_proficiency'),
        '자격증': self.data.get('certifications'),
    }

    for field_name, value in missing_fields.items():
        if not value:
            # Find field in document
            for para in self.doc.paragraphs:
                if field_name in para.text:
                    if '필수' in para.text:  # Required field
                        para.text = f"{field_name} : 정보 없음"
                    else:  # Optional field
                        para.text = ""  # Remove entirely
```

### Priority 3: Enhance Parser

**3.1 Better Experience Extraction**
```python
# File: scripts/resume_parser.py

def _parse_experience(self, lines):
    """Enhanced experience parsing"""
    experiences = []
    current_job = None
    current_project = None

    for line in lines:
        # Detect company/date header
        if self._looks_like_job_header(line):
            if current_job:
                experiences.append(current_job)
            current_job = self._extract_job_info(line)
            current_job['projects'] = []
            current_job['responsibilities'] = []
            current_project = None

        # Detect project within job
        elif self._looks_like_project_header(line):
            current_project = {
                'name': line,
                'responsibilities': []
            }
            if current_job:
                current_job['projects'].append(current_project)

        # Regular responsibility line
        elif current_job:
            clean_line = re.sub(r'^[•\-\*]\s*', '', line)
            if current_project:
                current_project['responsibilities'].append(clean_line)
            else:
                current_job['responsibilities'].append(clean_line)

    if current_job:
        experiences.append(current_job)

    return experiences

def _looks_like_project_header(self, line):
    """Detect project names within a job"""
    # Lines that end with dates in parentheses
    if re.search(r'\(20\d{2}\.\d{2}\s*-\s*.*?\)$', line):
        return True
    # Lines that start with project indicators
    if re.match(r'^[A-Z]{2,}.*구축|연구|개발', line):
        return True
    return False
```

**3.2 Calculate Experience Duration**
```python
def _calculate_experience_duration(self):
    """Calculate total career length"""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    total_months = 0
    for exp in self.extracted['experience']:
        start = self._parse_date_to_datetime(exp.get('start_date'))
        end_str = exp.get('end_date', 'Present')
        end = datetime.now() if end_str == 'Present' else self._parse_date_to_datetime(end_str)

        if start and end:
            delta = relativedelta(end, start)
            total_months += delta.years * 12 + delta.months

    years = total_months // 12
    months = total_months % 12

    self.extracted['metadata']['total_experience'] = {
        'years': years,
        'months': months,
        'formatted': f"{years}년 {months}개월"
    }
```

### Priority 4: Better Validation

**4.1 Check for Duplicates**
```python
# File: scripts/content_validator.py

def _check_for_duplicates(self):
    """Detect repeated content (like LinkedIn bug)"""
    lines = self.target_text.split('\n')
    duplicates = {}

    for i, line in enumerate(lines):
        if line.strip():
            count = lines.count(line)
            if count > 2:  # More than 2 occurrences
                duplicates[line[:50]] = count

    if duplicates:
        self.issues.append({
            'severity': 'CRITICAL',
            'type': 'duplicate_content',
            'message': 'Duplicate lines detected',
            'details': duplicates
        })
```

**4.2 Verify Critical Sections Filled**
```python
def _check_required_sections(self):
    """Ensure all required sections have actual data"""
    required_sections = {
        '경력 세부사항': False,
        '경력사항': False,
    }

    for section_name in required_sections:
        if section_name in self.target_text:
            # Check if followed by actual data (not placeholders)
            section_idx = self.target_text.index(section_name)
            next_100_chars = self.target_text[section_idx:section_idx+100]

            # If contains placeholder text, mark as not filled
            if '회사이름' in next_100_chars or '0000.00' in next_100_chars:
                required_sections[section_name] = False
                self.issues.append({
                    'severity': 'CRITICAL',
                    'type': 'section_not_filled',
                    'message': f'{section_name} section contains template placeholders'
                })
            else:
                required_sections[section_name] = True
```

---

## 📋 Test Results Summary

### What the Skill Did Right:
✅ Extracted personal information accurately
✅ Mapped education perfectly
✅ Created reasonable core competencies summary
✅ Organized technical skills well
✅ Handled missing birth date gracefully

### Critical Failures:
❌ LinkedIn URL duplicated 25+ times (critical bug)
❌ Detailed work experience section completely empty
❌ Career summary shows template placeholders
❌ Template placeholder text not removed
❌ Missing multiple work history entries

### Overall Assessment:
The skill shows promise in extraction and basic mapping, but has critical bugs in the template population logic that make it not production-ready. The core functionality (mapping detailed work experience) completely failed in this test.

**Recommendation**: Fix the three critical bugs before using in production:
1. LinkedIn duplication
2. Detailed experience mapping
3. Template cleanup

---

## 🎯 Success Metrics After Fixes

After implementing the recommended improvements, the skill should achieve:

| Metric | Current | Target |
|--------|---------|--------|
| Personal Info Accuracy | 95% | 98% |
| Education Mapping | 100% | 100% |
| Experience Detail Mapping | 0% | 95% |
| Template Cleanup | 30% | 95% |
| No Critical Bugs | 0% | 100% |
| **Overall Quality** | **60%** | **95%+** |

---

## 💡 Additional Enhancement Ideas

### Future Improvements (Nice to Have):

1. **Smart Content Fitting**
   - Auto-summarize experience if too long for template space
   - Prioritize recent roles over older ones
   - Keep quantified achievements always

2. **Multi-Language Support Enhancement**
   - Detect resume language automatically
   - Handle mixed Korean/English better
   - Offer translation option

3. **Template Learning**
   - Recognize template structure automatically
   - Build library of known templates (Meta Search, J&J, etc.)
   - Suggest best-match template

4. **Interactive Filling**
   - Prompt user for missing required fields during process
   - Show preview before final output
   - Allow field-by-field verification

5. **Confidence Scoring per Field**
   - Mark low-confidence fields visually in output
   - Generate detailed confidence report
   - Suggest manual review areas

---

## ✅ Conclusion

The resume-formatter skill has a solid foundation but needs critical bug fixes before production use. The extraction logic works well, but the template mapping and cleanup need significant improvement.

**Priority Actions:**
1. 🔴 Fix LinkedIn duplication bug (blocker)
2. 🔴 Implement detailed experience mapping (blocker)
3. 🔴 Fix career summary mapping (blocker)
4. 🟡 Improve template placeholder cleanup
5. 🟡 Add better validation checks

Once these are addressed, the skill will be production-ready and highly valuable for resume reformatting tasks.
