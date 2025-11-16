# Resume Formatter Skill

A robust Claude Code skill for reformatting resumes from one template to another while preserving content quality.

## Overview

This skill enables conversion of applicant resumes into specific company-required formats. It intelligently extracts content from diverse source resume layouts and maps them to target company templates.

**Key Features:**
- ✅ Handles multi-column layouts, headers/footers, text boxes, and tables
- ✅ Supports Korean and English resumes (mixed language too)
- ✅ Preserves quantified achievements and technical precision
- ✅ Graceful handling of missing information
- ✅ Comprehensive validation and quality checks
- ✅ Target accuracy: 94-96% for standard formats, 70-85% for edge cases

## Installation

Install the skill in Claude Code by adding the `resume-formatter.zip` file to your skills directory.

## Usage

In Claude Code, simply request resume reformatting:

```
"Convert this candidate's resume to the Meta Search format"
"Reformat my resume to match the J&J template"
"Map this resume to the company's required format"
```

Claude will:
1. Extract content from the source resume
2. Map it to the target template
3. Validate completeness
4. Provide a detailed report

## Components

### SKILL.md
Main skill instructions with comprehensive workflow guidance.

### references/
- `content_extraction_guide.md` - Strategies for extracting from diverse formats
- `template_field_mapping.md` - Mapping content to different template structures
- `quality_preservation.md` - Maintaining content quality during transformation

### scripts/
- `resume_parser.py` - Robust content extraction from .docx files
- `template_mapper.py` - Intelligent mapping to target templates
- `content_validator.py` - Quality validation and completeness checking

### tests/
Example resumes and templates for testing and development.

## Supported Formats

**Source Resumes:**
- Single-column chronological
- Multi-column layouts (2-3 columns)
- Table-based Korean resumes
- Free-form paragraph style
- Headers/footers with contact info
- Text boxes and shapes

**Target Templates:**
- Korean standard formats (Meta Search, J&J, AHR, etc.)
- Western chronological templates
- Functional/skills-based templates
- Custom company templates

## Edge Cases Handled

See `EDGE_CASES.md` for comprehensive documentation of:
- Multi-column reading order detection
- Headers/footers/text boxes extraction
- Non-standard section headings
- Date format normalization
- Korean-specific elements (age, military service, etc.)
- Missing information handling
- Content overflow strategies

## Accuracy Targets

| Resume Type | Complexity | Target Accuracy |
|------------|-----------|----------------|
| Standard chronological | Low | 94-96% |
| Table-based Korean | Low | 94-96% |
| Multi-column layouts | Medium | 85-92% |
| Headers/footers critical info | Medium | 85-91% |
| Creative/infographic | High | 70-82% |

## Quality Preservation

The skill maintains:
- ✓ Quantified achievements (percentages, metrics)
- ✓ Technical precision (specific tools, frameworks)
- ✓ Professional tone
- ✓ Complete contact information
- ✓ Recent experience with full detail

## Development

**Planning:** See `PLAN.md` for full implementation plan based on skill-creator guidelines.

**Testing:**
```bash
# Parse a resume
python scripts/resume_parser.py tests/format_before/resume.docx --output parsed.json

# Map to template
python scripts/template_mapper.py parsed.json tests/format_to/template.docx --output mapped.docx

# Validate
python scripts/content_validator.py parsed.json mapped.docx
```

## Requirements

- python-docx library (for scripts)
- Claude Code with skills support

## License

See LICENSE.txt (MIT License)

## Created

November 2025

Built following the [skill-creator](../skill-creator) guidelines for robust, production-ready Claude Code skills.
