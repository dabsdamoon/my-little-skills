# Resume Formatter - Changelog

## Version 1.2 (2025-11-17)

### CRITICAL Parser Fix

#### Korean Resume Format Support (FIXED)
- **Problem**: Parser failed to extract companies when date appears on separate line before company name
- **Example Format That Failed:**
  ```
  2023년 7월 - 현재
  Hudson AI - AI Researcher/Engineer
  ```
- **Root Cause**: Parser expected date and company on same line
- **Fix**: Added `_is_standalone_date_line()` and `_looks_like_company_line()` methods
  - Detects standalone date lines (Korean format: "YYYY년 MM월 - 현재")
  - Looks ahead to next line for company info
  - Merges date from line N with company from line N+1
- **File**: scripts/resume_parser.py:224-368
- **Impact**: CRITICAL - 0 companies extracted before fix, all companies extracted after
- **Test Result**: Now correctly extracts all 4 companies from Korean resume (Hudson AI, KRAFTON, 네오위즈, 케이엘넷)

#### Date Format Without Spaces (FIXED)
- **Problem**: Parser failed on dates like "2023년7월" (no space before month)
- **Example**: "2022년 9월 - 2023년7월" (notice no space before 7월)
- **Fix**: Changed regex from `\s+` to `\s*` (space optional)
- **File**: scripts/resume_parser.py:315
- **Impact**: HIGH - missed companies with this date format

### New Validator Features

#### Experience Years Comparison (NEW)
- **Feature**: Automatically compare total experience years between source and target
- **Functionality**:
  - Calculates total years from source metadata
  - Extracts and calculates total years from target document's 경력사항 section
  - Compares with 20% tolerance
  - Flags CRITICAL error if difference exceeds tolerance
- **Example Output**:
  ```
  CRITICAL: Experience years mismatch - Source: 9.8 years, Target: 0.8 years (diff: 9.0 years)
  ```
- **File**: scripts/content_validator.py:240-335
- **User Benefit**: Immediately detects when careers are missing from output

#### Missing Companies Detection (NEW)
- **Feature**: Flags companies that appear in source but missing in target
- **Functionality**:
  - Extracts company list from source data
  - Extracts company list from target 경력사항 section
  - Fuzzy matching (partial string match)
  - Lists all missing companies
- **Example Output**:
  ```
  CRITICAL: 3 companies missing from target: Hudson AI, 네오위즈, AI연구소, 케이엘넷
  ```
- **File**: scripts/content_validator.py:317-333
- **User Benefit**: Immediately see which careers were not transferred

### Testing Results

**Test Resume:** 이력서_v2025-10-26_sub_v1.0.docx (Korean format with 4 companies)

**Before v1.2:**
- Parser extracted: 0 companies ✗
- Validator: No experience comparison

**After v1.2:**
- Parser extracted: 4/4 companies ✓
  1. Hudson AI (2023.07 - Present)
  2. KRAFTON, Beluga Part (2022.09 - 2023.07)
  3. 네오위즈, AI연구소 (2018.04 - 2022.09)
  4. 케이엘넷 (2016.02 - 2018.04)
- Total experience calculated: 9.8 years ✓
- Validator: Detects missing companies and year mismatches ✓

### Package Details

**Version 1.2:**
- Package size: ~72 KB (was 69 KB in v1.1)
- Total files: 17
- Scripts updated:
  - resume_parser.py: +148 lines (new methods for Korean format)
  - content_validator.py: +96 lines (experience comparison)

### Migration from v1.1

To upgrade from v1.1:
1. Remove old resume-formatter.zip
2. Upload new resume-formatter.zip (v1.2)
3. No breaking changes - fully backward compatible
4. Korean format resumes will now work correctly

### Impact

This release fixes a **CRITICAL bug** that prevented the skill from working with Korean resumes that use the standard format of date-on-separate-line. Most Korean companies use this format, so this fix dramatically improves the skill's usability for the Korean market.

---

## Version 1.1 (2025-11-17)

### Critical Bug Fixes

#### 1. LinkedIn URL Duplication Bug (FIXED)
- **Problem**: LinkedIn URL was duplicated 25+ times in output
- **Root Cause**: No deduplication check when adding portfolio links in template_mapper.py
- **Fix**: Added `self.added_urls = set()` to track added URLs and prevent duplicates
- **File**: scripts/template_mapper.py:22, 257-261
- **Impact**: Critical - made output unusable

#### 2. Detailed Experience Section Empty (FIXED)
- **Problem**: 경력 세부사항 (detailed experience) section completely empty in output
- **Root Cause**: `_map_detailed_experience()` method not implemented
- **Fix**: Implemented complete method with:
  - Template section detection
  - Placeholder removal
  - Job block formatting with [회사소개] and [주요 업무/성과]
  - Project detection and grouping
- **File**: scripts/template_mapper.py:311-374
- **Impact**: Critical - core functionality missing

#### 3. Career Summary Not Filled (FIXED)
- **Problem**: 경력사항 showed template placeholders instead of actual companies
- **Root Cause**: `_map_career_summary()` not properly implemented
- **Fix**: Implemented proper mapping with company, title, dates from extracted data
- **File**: scripts/template_mapper.py:286-309
- **Impact**: Critical - required section not populated

#### 4. Template Placeholders Not Removed (FIXED)
- **Problem**: Template example text remained (fake companies, dates, qualifications)
- **Root Cause**: No cleanup logic for unfilled template text
- **Fix**: Implemented `_cleanup_template_placeholders()` with regex pattern matching
- **File**: scripts/template_mapper.py:376-417
- **Impact**: High - template text leaked into output

### Enhancements

#### Parser Improvements (scripts/resume_parser.py)
1. **Project Detection**: Added `_looks_like_project_header()` to detect projects within jobs
   - Recognizes brackets, project keywords, date ranges
   - Groups project responsibilities separately from general job duties
   - Lines 271-288

2. **Enhanced Experience Parsing**: Updated `_parse_experience()` to track projects
   - Creates nested project structure within jobs
   - Lines 224-269

3. **Total Experience Calculation**: Added `_calculate_total_experience_years()`
   - Uses python-dateutil for accurate date calculations
   - Handles "Present" end dates
   - Adds total_experience_years to metadata
   - Lines 527-570

#### Validator Enhancements (scripts/content_validator.py)
1. **Duplicate Detection**: Added `_check_for_duplicates()`
   - Detects repeated URLs (e.g., LinkedIn duplicated 25 times)
   - Finds repeated content (3+ occurrences)
   - Returns 0.0 score if duplicates found
   - Lines 142-168

2. **Required Section Check**: Added `_check_required_sections()`
   - Verifies 경력 세부사항, 경력사항, 인적사항 are filled
   - Checks for real content (not just template text)
   - Penalizes empty sections (-0.3) and missing sections (-0.2)
   - Lines 170-217

3. **Template Placeholder Check**: Added `_check_template_placeholders()`
   - Detects common Korean placeholders (OOO, XXX, 회사이름/부서명/직무)
   - Identifies fake company names (주식회사 ABC/DEF)
   - Returns 0.0 if placeholders remain
   - Lines 219-236

4. **Smart Recommendations**: Added `_generate_recommendations()`
   - Provides actionable fixes based on validation results
   - Prioritizes critical issues
   - Lines 238-268

5. **Enhanced Scoring**: Updated overall score calculation
   - Weighted: 70% completeness, 30% quality
   - More realistic assessment of output quality

### Documentation Updates

#### SKILL.md
- Added "Recent Improvements (v1.1)" section documenting all fixes
- Updated validation section with NEW quality checks
- Enhanced output description with quality scores

#### INSTALLATION.md
- Already existed from v1.0 (Korean filename fix)

#### CHANGELOG.md (NEW)
- This file - comprehensive change documentation

### Dependencies

Added requirement:
- `python-dateutil` - for accurate experience duration calculation

### Testing Results

**Before Fixes:**
- Overall Score: 60%
- LinkedIn duplicated 25+ times
- Detailed experience section: EMPTY
- Career summary: Template placeholders only
- Template cleanup: FAILED

**After Fixes (Tested 2025-11-17):**
- LinkedIn appears exactly once ✓
- Career summary filled with actual companies ✓
- Template placeholders removed ✓
- Duplicate detection working ✓
- Required section validation working ✓

### Package Details

**Version 1.1:**
- Package size: 66 KB (was 55 KB in v1.0)
- Total files: 17 (same as v1.0)
- Scripts size increased due to enhancements:
  - template_mapper.py: 690 lines (was ~150 lines)
  - resume_parser.py: 604 lines (was ~544 lines)
  - content_validator.py: 317 lines (was ~189 lines)

### Migration from v1.0

To upgrade from v1.0:
1. Remove old resume-formatter.zip
2. Upload new resume-formatter.zip
3. No breaking changes - fully backward compatible
4. Ensure python-dateutil is installed: `pip install python-dateutil`

### Known Limitations

1. Parser may struggle with resumes that use:
   - Complex multi-column layouts (especially 3+ columns)
   - Heavy use of text boxes for content
   - Scanned/image-based resumes (no text to extract)

2. Template mapper assumes:
   - Target template has standard Korean sections
   - Template uses similar structure (table or paragraph-based)

3. Validator strict mode may flag false positives:
   - Some templates use different section names
   - Adjust validation criteria if needed for non-standard templates

### Future Improvements

Potential enhancements for v1.2+:
1. OCR support for scanned resumes
2. Support for more template types (Western chronological, functional)
3. AI-powered content summarization for overflow
4. Multi-language support beyond Korean/English
5. Photo extraction and resizing
6. Better handling of non-standard section names

---

## Version 1.0 (2025-11-16)

### Initial Release

**Features:**
- Resume content extraction from .docx files
- Template mapping to company formats
- Content validation with completeness scoring
- Support for Korean and English resumes
- Multi-source extraction (headers, footers, tables, text boxes)

**Known Issues (Fixed in v1.1):**
- Korean filenames in zip caused upload errors (FIXED in v1.0)
- LinkedIn URL duplication bug (FIXED in v1.1)
- Detailed experience section not mapped (FIXED in v1.1)
- Template placeholders not removed (FIXED in v1.1)
