# Resume Formatter - Installation & Troubleshooting

## Installation

### Option 1: Upload to Claude Code (Recommended)

1. Download the skill package:
   ```
   resume-formatter/resume-formatter.zip
   ```

2. In Claude Code, upload the skill:
   - Open Claude Code settings/skills section
   - Upload `resume-formatter.zip`
   - The skill will be installed and ready to use

3. Verify installation:
   - The skill should appear in your available skills
   - Name: `resume-formatter`
   - Description: "This skill should be used when users request reformatting..."

### Option 2: Use from Directory

If Claude Code is already configured to use the `anthropic-skills` directory:
- The skill is automatically available
- No installation needed
- Just start using it!

## Fixed Issues

### ✅ Korean Filename Error - RESOLVED

**Problem:** Original package included test files with Korean characters in filenames:
- `이력서_v2025-10-26_sub_v1.0.docx`
- `메타써치_국문이력서_샘플.docx`
- `이력서 양식(JnJ)_template.doc`

This caused: `Zip file contains path with invalid characters`

**Solution:**
- Removed test files from the packaged skill
- Created clean package with only ASCII-safe filenames
- Test files remain in your local directory but excluded from zip
- Added to `.gitignore` to prevent future issues

**Current Package Contents:**
```
✓ SKILL.md - Main skill instructions
✓ README.md - User documentation
✓ LICENSE.txt - MIT License
✓ PLAN.md - Implementation plan
✓ EDGE_CASES.md - Edge case documentation
✓ USAGE_EXAMPLE.md - Usage examples
✓ references/ - 3 reference guides
✓ scripts/ - 3 Python scripts
✓ tests/README.md - Placeholder for test files
```

**File Size:** 149 KB (clean, no binary files)

## Using Your Test Files

Your original test files are still available locally at:
```
/Users/dabsdamoon/projects/anthropic-skills/resume-formatter/tests/format_before/
/Users/dabsdamoon/projects/anthropic-skills/resume-formatter/tests/format_to/
```

To use them with the skill:
1. Open Claude Code
2. Attach your test files directly to your request
3. Claude will process them using the skill

Example:
```
"Convert this resume to the Meta Search format"

[Attach files:]
- /path/to/tests/format_before/이력서_v2025-10-26_sub_v1.0.docx
- /path/to/tests/format_to/메타써치_국문이력서_샘플.docx
```

## Troubleshooting

### Issue: Skill not showing up in Claude Code

**Solution:**
1. Check that the zip was uploaded successfully
2. Verify file size is ~149 KB
3. Try re-uploading
4. Check Claude Code logs for errors

### Issue: Scripts not working

**Symptoms:** Python errors when using the skill

**Solution:**
Ensure `python-docx` is installed:
```bash
pip3 install python-docx
```

The skill will prompt you if this dependency is missing.

### Issue: Korean text looks garbled

**Symptoms:** Korean characters appear as � or boxes

**Solution:**
- This is an encoding issue
- The skill handles UTF-8 and EUC-KR automatically
- If problems persist, save source resume as UTF-8 in Word
- File → Save As → More Options → Encoding: UTF-8

### Issue: Extraction confidence low

**Symptoms:** Validation report shows <70% confidence

**Possible causes:**
1. Source resume has unusual format
2. Missing standard sections
3. Content in text boxes or graphics
4. Scanned/image-based resume

**Solution:**
- Provide additional context to Claude
- Manually specify missing information
- For scanned resumes, convert to text first (OCR)

### Issue: Template mapping incomplete

**Symptoms:** Some fields not populated in target

**Possible causes:**
1. Source resume missing that information
2. Field name not recognized
3. Content couldn't fit

**Solution:**
- Review validation report for specifics
- Provide missing information to Claude
- Accept intelligent summarization for overflow content

## Verification

After installation, verify the skill works:

**Test command:**
```
"I need help reformatting a resume to a company template"
```

**Expected:** Claude should recognize this as a resume-formatter task and offer to help with the skill.

## Support

If issues persist:
1. Check `resume-formatter/USAGE_EXAMPLE.md` for detailed examples
2. Review `resume-formatter/PLAN.md` for implementation details
3. Examine `resume-formatter/EDGE_CASES.md` for known limitations

## Package Details

**Current Version:** 1.0 (2025-11-16)

**Package Contents:**
- 13 files total
- 149,311 bytes (146 KB)
- All ASCII-safe filenames
- No binary files included

**Checksum:**
```bash
# Verify package integrity
unzip -l resume-formatter.zip
# Should show 13 files
```

## Next Steps

1. ✅ Install the clean package
2. ✅ Test with a sample request
3. ✅ Use your Korean test files by attaching them directly
4. ✅ Enjoy automated resume reformatting!
