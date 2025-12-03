# Quality Preservation Guide

This guide ensures content quality is maintained or improved during resume reformatting.

## Core Principles

### 1. Achievement-Focused Language

**Preserve quantified achievements and impact**:
```
✓ GOOD (Preserve these):
- "Increased model accuracy from 87% to 95% using ensemble methods"
- "Reduced system latency by 40% through cache optimization"
- "Led team of 5 engineers delivering $2M revenue project"
- "Processed 10M daily transactions with 99.99% uptime"

✗ WEAK (Avoid diluting to these):
- "Improved model performance"
- "Optimized system"
- "Managed engineering team"
- "Handled transactions"
```

**When summarizing, prioritize**:
1. **Quantified metrics** (percentages, dollar amounts, scale)
2. **Business impact** (revenue, cost savings, efficiency gains)
3. **Technical specifics** (tools, frameworks, methodologies)
4. **Scope/scale** (team size, user base, data volume)

**Strong action verbs hierarchy**:

**Tier 1 - Leadership/Innovation** (Preserve in summaries):
- Architected, Designed, Invented, Pioneered, Spearheaded, Drove, Led, Founded, Established

**Tier 2 - Execution/Delivery** (Keep when possible):
- Developed, Implemented, Engineered, Built, Created, Deployed, Launched, Delivered, Executed

**Tier 3 - Support/Maintenance** (Replace if space limited):
- Maintained, Supported, Assisted, Helped, Participated, Contributed

### 2. Technical Precision

**Preserve specific technical terminology**:
```
✓ GOOD (Keep specifics):
- "PyTorch 2.0 with CUDA optimization"
- "AWS Lambda with DynamoDB"
- "React 18 with TypeScript and Redux Toolkit"
- "Transformer architecture with 8-bit quantization"

✗ WEAK (Don't generalize to):
- "Machine learning framework"
- "Cloud services"
- "Frontend development"
- "Neural network"
```

**Technical details to preserve**:
- Specific tools/frameworks with versions
- Architecture patterns and design choices
- Performance metrics (latency, throughput, accuracy)
- Scale indicators (data size, user count, traffic volume)
- Certifications and specialized knowledge

### 3. Professional Tone

**Maintain consistent professional register**:
- Formal but not overly stiff
- Active voice preferred
- Past tense for previous roles, present for current
- No first-person pronouns (I, me, my)
- No casual language or slang

**Example transformations**:
```
Before: "I was responsible for making sure the ML models worked well"
After:  "Optimized ML model performance achieving 95% accuracy"

Before: "Helped out with the team's projects and stuff"
After:  "Contributed to cross-functional projects delivering key features"

Before: "Did some coding in Python and worked with databases"
After:  "Developed Python applications with PostgreSQL backend"
```

### 4. Completeness Over Brevity

**Never drop critical information**:
- Contact information (phone, email)
- Recent work experience (last 5 years minimum)
- Highest education degree
- Key technical skills for the role

**Prioritization when space limited**:
1. **Must keep**: Name, contact, recent experience (3+ years), top skills
2. **Should keep**: All experience (10+ years), education details, certifications
3. **Can summarize**: Older roles (10+ years ago), minor projects, hobbies
4. **Can drop**: Outdated skills, irrelevant experience, excessive details

## Content Transformation Strategies

### Summarization While Preserving Impact

**Original** (250 characters):
```
Architected and deployed end-to-end training and inference pipeline for multilingual TTS models, reducing inference latency by 40% and improving perceptual audio quality metrics (MOS, PESQ). Implemented automated data preprocessing pipeline handling 50+ languages with IPA phonemization, enabling 3x faster model iteration cycles.
```

**Summarized** (150 characters):
```
Architected TTS pipeline for 50+ languages, reducing latency 40% and improving audio quality (MOS/PESQ). 3x faster iteration via automated preprocessing.
```

**What was preserved**:
- Core action (Architected)
- System scope (TTS, multilingual)
- Metrics (40% latency reduction, 3x faster)
- Technical specifics (MOS, PESQ, IPA)

**What was condensed**:
- "end-to-end training and inference pipeline" → "pipeline"
- "perceptual audio quality metrics" → "audio quality"
- "automated data preprocessing pipeline handling" → "automated preprocessing"

### Multiple Bullets to Single Summary

**Original** (5 bullets, 800 chars):
```
• Developed ML models for speech synthesis achieving state-of-the-art quality
• Implemented custom vocoders from scratch improving generation speed
• Built data processing pipelines handling diverse audio formats
• Optimized inference performance for production deployment
• Collaborated with product team to define model requirements
```

**Summarized** (1-2 bullets, 300 chars):
```
• Developed state-of-the-art speech synthesis models with custom vocoders, optimizing for production with improved generation speed
• Built data pipelines handling diverse audio formats, collaborating cross-functionally on requirements
```

### Condensing Older Experience

**Original** (detailed, from 10 years ago):
```
Software Engineer | Old Company | 2013-2015
• Developed Java web applications using Spring Framework
• Maintained legacy codebases and fixed bugs
• Participated in code reviews and team meetings
• Contributed to documentation and testing
```

**Condensed**:
```
Software Engineer | Old Company | 2013-2015
Developed Java/Spring web applications, maintained legacy systems
```

**Rationale**: Older experience gets brief treatment; focus space on recent roles.

## Handling Overflow Content

### Strategy 1: Intelligent Prioritization

When experience exceeds template capacity:

**Step 1: Categorize roles by relevance**
```python
def prioritize_experience(roles, target_field):
    """Assign priority scores to experience entries"""
    for role in roles:
        score = 0
        # Recency (most important)
        years_ago = current_year - role.end_year
        if years_ago < 3: score += 10
        elif years_ago < 5: score += 7
        elif years_ago < 10: score += 4
        else: score += 1

        # Relevance (technical role = more relevant for tech resume)
        if is_relevant(role.title, target_field):
            score += 5

        # Impact (quantified achievements)
        if has_metrics(role.responsibilities):
            score += 3

        role.priority = score

    return sorted(roles, key=lambda r: r.priority, reverse=True)
```

**Step 2: Allocate space by priority**
```
High priority roles (recent, relevant): Full detail (4-6 bullets each)
Medium priority roles: Condensed (2-3 bullets)
Low priority roles: One-line summary or omit
```

### Strategy 2: Tiered Detail Levels

**Full Detail** (for most recent/relevant roles):
```
AI Research Engineer | Hudson AI | 2023.07 - Present
• Architected multilingual TTS pipeline reducing inference latency 40%
• Improved perceptual audio quality (MOS, PESQ) through custom vocoder optimization
• Built data preprocessing automation handling 50+ languages with IPA phonemization
• Developed reference-based TTS with intelligent audio selection algorithms
• Led PULSE dialogue engine with automated character generation and RAG-based memory
```

**Condensed** (for older/less relevant roles):
```
Software Engineer | Previous Company | 2019-2021
Developed Python/Django web applications, implemented REST APIs, managed AWS infrastructure
```

**One-line** (for very old or brief roles):
```
Junior Developer | Startup Inc | 2015-2016 (Full-stack development, Python/JavaScript)
```

### Strategy 3: Merge Similar Roles

**Original** (3 short consultingcontract roles):
```
ML Consultant | Client A | 2022.01-2022.03
ML Consultant | Client B | 2022.04-2022.06
ML Consultant | Client C | 2022.07-2022.09
```

**Merged**:
```
ML Consulting | Multiple Clients | 2022.01-2022.09
Delivered ML solutions for clients in healthcare, finance, and e-commerce. Key achievements:
• Improved prediction accuracy 25% for Client A using ensemble methods
• Reduced model training time 60% for Client B through pipeline optimization
```

## Quality Checks

### Before Finalizing, Verify:

**1. No Information Loss in Critical Areas**
```python
def validate_critical_info(source, target):
    checks = {
        'name': source.name == target.name,
        'contact': (source.phone in target) or (source.email in target),
        'recent_experience': has_last_n_years(target, n=3),
        'education': has_highest_degree(target),
        'key_skills': top_skills_present(source, target, threshold=0.8)
    }
    return all(checks.values())
```

**2. Metrics Preserved**
- All percentages maintained
- Dollar amounts accurate
- Scale indicators (team size, users, data volume) present
- Time periods correct

**3. Technical Terms Intact**
- Framework names not generalized
- Tool names specific
- Certifications exact
- No autocorrect damage (PyTorch → Python Torch)

**4. Professional Language**
- No grammatical errors introduced
- Consistent verb tenses
- No casual language
- Proper capitalization

**5. Formatting Consistent**
- Bullet points aligned
- Date formats standardized
- No orphaned text
- Proper spacing

## Language-Specific Quality

### Korean Resumes

**Formal Language (존댓말)**:
- Use formal verb endings when appropriate
- Maintain professional register
- No casual speech patterns

**Technical Term Handling**:
```
Option 1 - Keep English: PyTorch, AWS, React (common in tech)
Option 2 - Korean + English: 파이토치(PyTorch), 딥러닝(Deep Learning)
Option 3 - Korean only: 기계학습, 인공지능 (less common for tools)

Best practice: Keep well-known English tech terms as-is
```

**Date Format Consistency**:
```
Standard: YYYY.MM or YYYY년 MM월
Example: 2023.07 or 2023년 7월
Periods: ~ (tilde) or - (dash)
Present: 현재, 재직중
```

### English Resumes

**American vs. British Spelling**:
- Maintain consistency throughout
- American: optimize, analyze, center
- British: optimise, analyse, centre

**Date Formats**:
```
American: MM/YYYY or Month YYYY
Example: 07/2023 or July 2023
Present: Present, Current
```

## Achievement Enhancement

In some cases, original resume language is weak. If space allows, strengthen:

**Original**: "Responsible for ML model development"
**Enhanced**: "Developed ML models achieving 95% accuracy, deployed to production serving 1M+ users"

**Original**: "Worked on team projects"
**Enhanced**: "Collaborated in cross-functional team of 8 delivering $2M revenue product"

**Original**: "Used Python and databases"
**Enhanced**: "Developed Python applications with PostgreSQL, processing 100K daily transactions"

**When to enhance**:
- Generic descriptions → Add specifics
- Missing metrics → Infer reasonable estimates if context allows
- Weak verbs → Upgrade to stronger verbs
- **Always verify with user before adding information not in source**

## Red Flags to Avoid

**Don't**:
- ❌ Invent achievements not in source
- ❌ Exaggerate numbers or metrics
- ❌ Generalize technical terms excessively
- ❌ Remove all older experience (keep at least summary)
- ❌ Change meaning of accomplishments
- ❌ Add skills not mentioned in source
- ❌ Alter dates or timelines
- ❌ Introduce grammatical errors

**Do**:
- ✓ Preserve exact metrics from source
- ✓ Keep technical terminology specific
- ✓ Maintain chronological accuracy
- ✓ Verify all mapped content matches source
- ✓ Flag any ambiguities for user review
- ✓ Ask user before dropping significant content
- ✓ Strengthen weak language if meaning unchanged

## Quality Validation Checklist

Before delivery, confirm:

- [ ] All critical fields populated (name, contact, recent experience)
- [ ] Quantified achievements preserved (percentages, amounts, scale)
- [ ] Technical terms specific and accurate (tools, frameworks, versions)
- [ ] Strong action verbs used (Tier 1 & 2)
- [ ] Professional tone throughout
- [ ] No grammatical errors
- [ ] Dates formatted consistently
- [ ] No text truncated mid-sentence
- [ ] Formatting clean (bullets, spacing, alignment)
- [ ] Recent experience (3-5 years) has full detail
- [ ] Older experience at least summarized
- [ ] Education includes degree, school, year minimum
- [ ] Top skills listed (technical, languages)
- [ ] No placeholder text remaining (unless intentional for missing info)
- [ ] Korean text displays correctly (no encoding issues)
- [ ] Contact information accurate and complete

## Example: Full Transformation

**Source** (free-form resume, 3 pages):
```
문다빈
AI Researcher / Engineer
Phone: 010-9860-8431 | Email: dabs.damoon@gmail.com

기술 스택
- ML/DL Frameworks: PyTorch, TensorFlow, Scikit-Learn, JAX
- Audio Processing: librosa, torchaudio, nnAudio, soundfile, pydub
- MLOps: AWS (EC2, S3, Lambda), GCP, Docker, Git, MLflow
- LLM/Agents: LangChain, Claude, Gemini, OpenAI API, RAG systems

경력
Hudson AI - AI Researcher/Engineer (2023.07 - 현재)

[많은 상세 내용... 10+ bullet points per project]
```

**Target** (Meta Search template, 1 page):
```
지원분야: AI/ML Engineer

인적사항
성    명: 문다빈
생년/성별: 정보 없음
주    소: 서울특별시 서초구
연 락 처: 010-9860-8431 / dabs.damoon@gmail.com

핵심역량
• ML/DL Frameworks (PyTorch, TensorFlow) 활용한 음성 synthesis 모델 개발 경험
• AWS/GCP MLOps 파이프라인 구축 및 production 배포 경험
• LLM/RAG 시스템 개발 및 prompt engineering 전문성

경력사항 (총 1년 6개월)
2023.07 ~ 재직중    Hudson AI / AI Research / AI Researcher/Engineer

상세경력사항
2023.07 ~ 재직중 (1년 6개월)        Hudson AI / AI Research / AI Researcher

[AI/ML 스타트업, 직원수 약 50명]

[주요업무]
• 다국어 TTS 모델 학습 파이프라인 구축, 추론 latency 40% 감소 달성
• Vocoder from-scratch 개발 및 최적화로 음질 향상 (MOS, PESQ)
• PULSE 대화 엔진 구축: RAG 기반 memory system 구현으로 대화 맥락 유지
• LangChain 활용 multi-LLM (Claude/Gemini/GPT) 최적화 및 hyperparameter tuning
• 50+ 언어 지원 데이터 전처리 자동화 파이프라인 개발 (IPA phonemization)
```

**Quality preserved**:
- ✓ All contact info maintained
- ✓ Technical skills preserved (PyTorch, AWS, RAG, etc.)
- ✓ Quantified achievements kept (40% latency reduction)
- ✓ Specific metrics (MOS, PESQ, 50+ languages)
- ✓ Professional Korean terminology
- ✓ Strong action verbs (구축, 달성, 구현, 개발)

**Adaptations made**:
- Condensed from 10+ bullets to 5 key achievements
- Grouped related accomplishments
- Formatted dates to template convention (YYYY.MM)
- Added company context ([AI/ML 스타트업...])
- Marked missing info ("생년/성별: 정보 없음")
