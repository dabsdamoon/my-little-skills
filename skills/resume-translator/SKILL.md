---
name: resume-translator
description: This skill should be used when users request translation of resumes or CVs between English and Japanese, Korean, or Chinese. It handles Word document (.docx) format resumes and offers options to preserve the original formatting or create a culturally-appropriate format based on target language conventions.
---

# Resume Translator

## Overview

This skill enables translation of resumes between English and Japanese, Korean, or Chinese while preserving professional quality. It processes Word document (.docx) files and provides two formatting approaches: maintaining the original resume structure or adapting to culturally-appropriate conventions for the target language region.

## Translation Quality Principles

**CRITICAL**: Always prioritize impact-focused, achievement-oriented language over generic descriptions. Apply these principles to ALL translations:

### 1. Achievement vs. Responsibility Language

**Strong (Achievement-focused):**
- "Architected and deployed full workflow" (not just "Built pipeline")
- "Designed and implemented training-to-inference system achieving 40% latency reduction"
- "Invented automated method reducing processing time by 60%"
- "Drove measurable revenue lift of 15% through ML model optimization"

**Weak (Responsibility-focused - AVOID):**
- "Built data processing pipeline"
- "Implemented feature"
- "Responsible for system maintenance"
- "Worked on team project"

### 2. Quantifiable Business Impact

Always preserve or enhance metrics and business outcomes:
- Performance improvements (latency, throughput, accuracy, quality metrics)
- Business metrics (revenue, conversion, user growth, cost savings)
- Scale indicators (number of users, data volume, system capacity)
- Time/efficiency gains

### 3. Technical Precision

Use specific technical terminology, not vague descriptions:
- "cosine-similarity search with prompt-caching" (not "similarity search")
- "perceptual audio quality metrics (MOS, PESQ)" (not "quality improvements")
- "transformer-based architecture with 8-bit quantization" (not "neural network model")

### 4. Action Verbs Hierarchy

**Tier 1 (Preferred for senior/impactful work):**
- Architected, Designed, Invented, Pioneered, Spearheaded, Drove, Led

**Tier 2 (For implementation work):**
- Developed, Implemented, Engineered, Optimized, Automated

**Tier 3 (Avoid - too weak):**
- Built, Made, Worked on, Helped with, Assisted

## Role-Type Considerations

### Technical Roles (AI/ML, Engineering, Data Science)
**DO:**
- Focus entirely on technical achievements, metrics, and business impact
- Use precise technical terminology
- Highlight scalability, performance, and innovation
- Include links to demos, papers, or portfolios

**DO NOT:**
- Add lengthy personal statements about "passion" or "values"
- Include generic self-descriptions
- Waste space on subjective personality traits
- Use vague technical descriptions

### Non-Technical Roles (Management, Sales, HR, Marketing)
- May include brief (2-3 line) professional summary if culturally appropriate
- Balance soft skills with quantifiable achievements
- Still emphasize business outcomes and metrics

## Workflow Decision Tree

When a user requests resume translation, follow this decision tree:

1. **Identify source and target languages**
   - Supported pairs: English↔Japanese, English↔Korean, English↔Chinese (Simplified/Traditional)
   - If unsure about the source language, analyze the document to detect it
   - If the target language is not specified, ask the user

2. **Identify role type and seniority**
   - Technical vs. non-technical role
   - Entry-level vs. mid-career vs. senior position
   - This determines whether personal statements are appropriate

3. **Determine formatting approach**
   - Ask the user: "Would you like to (1) maintain the original resume format, or (2) adapt the format to be more suitable for [target language/region] conventions?"
   - If maintaining original format → Proceed to Format-Preserving Translation
   - If adapting format → Proceed to Culture-Adapted Translation

4. **Process the document**
   - Follow the appropriate workflow below based on the formatting decision

## Format-Preserving Translation

When maintaining the original format:

1. **Read the source document**
   - Use available tools to read the .docx file content
   - Preserve the document structure: sections, bullet points, formatting, tables
   - Identify the role type to apply appropriate quality principles

2. **Translate content with quality enhancement**
   - **Apply Translation Quality Principles** (see above) to EVERY bullet point
   - Translate all text content while:
     - **Strengthening weak action verbs** to Tier 1/2 verbs
     - **Preserving or enhancing metrics and business impact**
     - **Maintaining technical precision** with specific terminology
     - **Converting responsibility statements to achievement statements** when possible
   - Section-specific translation:
     - Section headings (e.g., "Experience," "Education," "Skills")
     - Job titles and company names (translate or romanize as culturally appropriate)
     - Descriptions and bullet points (ENHANCE with stronger language)
     - Date formats (adapt to target language conventions: MM/YYYY for Western, YYYY年MM月 for Japanese, etc.)

3. **Maintain formatting elements**
   - Keep the same visual structure
   - Preserve bold, italic, and other text styling
   - Maintain bullet point styles and indentation
   - Keep table structures intact
   - Preserve any portfolio/demo/publication links

4. **Quality checks**
   - Verify every bullet uses strong action verbs (Tier 1 or 2)
   - Confirm metrics and outcomes are preserved/enhanced
   - Ensure technical terminology is precise and specific
   - Check no generic personal statements were added (especially for technical roles)
   - Verify dates, numbers, and proper nouns are handled correctly
   - Ensure contact information and links are clearly presented

## Culture-Adapted Translation

When adapting to target language conventions, consult the reference materials in `references/` for region-specific best practices:

- `references/japanese_resume_practices.md` - For Japanese resumes (履歴書/職務経歴書)
- `references/korean_resume_practices.md` - For Korean resumes (이력서)
- `references/chinese_resume_practices.md` - For Chinese resumes (简历/履歷)

### Adaptation Process

1. **Read source document and reference materials**
   - Extract all content from the source .docx file
   - Load the appropriate reference file for the target language
   - Understand the cultural conventions for resume structure in that region
   - **Identify role type** - technical vs. non-technical

2. **Restructure content**
   - Reorganize sections according to target language conventions
   - Examples of regional differences:
     - Japanese: May require separate 履歴書 (rirekisho) and 職務経歴書 (shokumukeirekisho)
     - Korean: Often includes personal information (photo, family details) not common in Western resumes
     - Chinese: May emphasize educational background more prominently

3. **Translate with cultural context AND quality principles**
   - **CRITICAL**: Apply all Translation Quality Principles even when adapting format
   - Use professional terminology standard in the target region
   - Adapt job titles to equivalent terms used in that region's job market
   - **Translate achievement statements with strong action verbs and metrics**
   - Translate company descriptions when the organization may be unfamiliar to target audience
   - Format dates according to regional standards
   - Adjust tone and phrasing to match regional professional norms
   - **Preserve all technical precision and business impact metrics**

4. **Apply formatting conventions (with caution)**
   - Use standard section ordering for the target region
   - Apply appropriate font choices (e.g., MS Mincho/Gothic for Japanese)
   - Adjust layout to match regional expectations
   - Include or exclude personal information as culturally appropriate

   **Personal Statement / Self-Assessment Section:**
   - **For technical roles (AI/ML, Engineering, Data Science)**:
     - **SKIP or MINIMIZE** this section entirely
     - If the target culture expects it, limit to 1-2 sentences focused on technical domain and scale
     - NEVER add generic statements about "passion," "responsibility," or personality traits
   - **For non-technical roles**:
     - May include brief (2-3 line) professional summary if culturally required
     - Focus on quantifiable achievements and value proposition
     - Avoid flowery, generic language

5. **Quality checks**
   - Verify every bullet uses achievement-oriented language with Tier 1/2 action verbs
   - Confirm all metrics and business outcomes are preserved
   - Ensure technical terminology remains precise and specific
   - **Check personal statement is absent or minimal for technical roles**
   - Verify the resume follows target region's professional standards
   - Ensure all critical information is accurately translated
   - Check that the format would be well-received by employers in the target region

## Translation Examples: Strong vs. Weak

### English → Japanese

**WEAK (Avoid):**
❌ "データ処理パイプラインを構築した" (Built data processing pipeline)
❌ "機能を実装した" (Implemented feature)
❌ "プロジェクトに取り組んだ" (Worked on project)

**STRONG (Use these patterns):**
✅ "エンドツーエンドの学習・推論ワークフローを設計・構築し、推論レイテンシを40%削減" (Architected and deployed end-to-end training-to-inference workflow, reducing inference latency by 40%)
✅ "自動化手法を発明し、処理時間を60%短縮、知覚音質の測定可能な向上を実現" (Invented automated method reducing processing time by 60% while achieving measurable gains in perceptual audio quality)
✅ "コサイン類似度検索とプロンプトキャッシングを実装し、レイテンシとコストを大幅削減" (Implemented cosine-similarity search with prompt-caching for significant latency and cost savings)

### English → Korean

**WEAK (Avoid):**
❌ "데이터 파이프라인을 구축했습니다" (Built data pipeline)
❌ "시스템을 유지보수했습니다" (Maintained system)
❌ "팀 프로젝트에 참여했습니다" (Participated in team project)

**STRONG (Use these patterns):**
✅ "전체 학습-추론 워크플로우를 설계 및 배포하여 추론 지연시간 40% 감소 달성" (Designed and deployed full training-to-inference workflow, achieving 40% reduction in inference latency)
✅ "ML 모델 최적화를 통해 측정 가능한 15% 매출 증대 주도" (Drove measurable 15% revenue lift through ML model optimization)
✅ "대규모 데이터 전처리 자동화 시스템 개발, 처리 효율 60% 향상" (Developed large-scale data preprocessing automation, improving processing efficiency by 60%)

### English → Chinese

**WEAK (Avoid):**
❌ "构建了数据管道" / "建置了資料管道" (Built data pipeline)
❌ "实现了功能" / "實作了功能" (Implemented feature)
❌ "参与项目开发" / "參與專案開發" (Participated in project development)

**STRONG (Use these patterns):**
✅ "设计并部署端到端训练-推理工作流，将推理延迟降低40%" / "設計並部署端到端訓練-推理工作流程，將推理延遲降低40%" (Designed and deployed end-to-end training-to-inference workflow, reducing inference latency by 40%)
✅ "发明自动化方法，在减少60%处理时间的同时实现可测量的感知音质提升" / "發明自動化方法，在減少60%處理時間的同時實現可測量的感知音質提升" (Invented automated method reducing processing time by 60% while achieving measurable perceptual audio quality gains)
✅ "通过ML模型优化推动可测量的15%收入增长" / "透過ML模型最佳化推動可測量的15%營收成長" (Drove measurable 15% revenue lift through ML model optimization)

## Language-Specific Considerations

### Japanese Translation
- Distinguish between 履歴書 (rirekisho - formal resume) and 職務経歴書 (shokumukeirekisho - career history)
- Use appropriate keigo (respectful language) for professional context
- **Use achievement-focused verbs**: 設計・構築した, 開発・実装した, 主導した, 達成した
- Consider whether to use kanji, hiragana, or katakana for foreign names and terms
- Preserve technical English terms when commonly used in Japanese tech industry (e.g., pipeline, latency, ML)
- Dates: Use 年/月 format or Western YYYY/MM depending on context
- **For 自己PR section**: Keep minimal for technical roles, focus on quantifiable technical achievements

### Korean Translation
- Use appropriate honorifics and formal language (존댓말)
- **Use achievement-focused verbs**: 설계 및 구축, 개발 및 구현, 주도, 달성
- Handle name order (family name first in Korean)
- Preserve technical terminology with Korean translations in parentheses when first introduced
- Consider inclusion of Korean age vs. international age if relevant
- Dates: Use YYYY.MM or YYYY년 MM월 format
- **For 자기소개 section**: Minimize or skip for technical roles

### Chinese Translation
- Determine if Simplified (简体) or Traditional (繁體) Chinese is needed
- Use formal/professional register (书面语)
- **Use achievement-focused verbs**: 设计并实现/設計並實現, 开发/開發, 主导/主導, 推动/推動
- Handle proper nouns appropriately (transliteration vs. translation)
- Maintain technical precision with specific terminology
- Dates: Use YYYY年MM月 format
- **For 自我评价 section**: Keep very brief (1-2 sentences) for technical roles, focus on domain expertise and scale

## Output Format

After completing the translation:

1. Create a new .docx file with the translated content
2. Name the file appropriately (e.g., `resume_japanese.docx`, `resume_translated_zh.docx`)
3. Provide a brief summary of:
   - Languages translated (from → to)
   - Formatting approach used (preserved original or adapted)
   - Any notable adaptations or decisions made
   - Suggestions for the user to review (e.g., verify company names, personal information)

## Resources

### references/
This skill includes region-specific reference materials that provide detailed guidance on resume conventions, formatting standards, and cultural expectations for each target language region. Load these files as needed when performing culture-adapted translations.
