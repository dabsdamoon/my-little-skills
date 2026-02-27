# Debugging Retrospective Template

Use this structure for retrospective documents.

---

## [Title: Brief description of the bug]

**Date**: [Date of debugging session]
**Duration**: [Approximate time spent]
**Severity**: [Impact level: Critical/High/Medium/Low]

---

### 1. Problem Summary

**What happened**: [1-2 sentence description of the observed issue]

**Expected behavior**: [What should have happened]

**Actual behavior**: [What actually happened]

**Impact**: [Who/what was affected]

---

### 2. Initial Symptoms

List observable symptoms that led to investigation:

- [Symptom 1: e.g., "Error message X appeared when..."]
- [Symptom 2: e.g., "Feature Y stopped working after..."]
- [Symptom 3: e.g., "Performance degraded when..."]

---

### 3. Investigation Timeline

Document the debugging flow chronologically:

#### Hypothesis 1: [What was suspected]
- **Investigation**: [What was checked]
- **Finding**: [What was discovered]
- **Result**: [Confirmed/Ruled out] - [Why]

#### Hypothesis 2: [Next theory]
- **Investigation**: [What was checked]
- **Finding**: [What was discovered]
- **Result**: [Confirmed/Ruled out] - [Why]

[Continue for each hypothesis tested]

---

### 4. Root Cause

**The actual cause**: [Clear explanation of what caused the issue]

**Why it happened**: [Contributing factors, conditions that led to this]

**Why it wasn't obvious**: [What made this hard to find]

---

### 5. Solution

**Fix implemented**: [What was changed]

```
[Code diff or key changes if applicable]
```

**Why this works**: [Explanation of how the fix addresses the root cause]

**Verification**: [How the fix was confirmed to work]

---

### 6. Lessons Learned

#### Technical Insights
- [Specific technical knowledge gained about the language/framework/system]

#### Debugging Strategies That Worked
- [Approaches that helped find the issue]

#### What Didn't Work
- [Approaches that wasted time and why]

#### Red Herrings
- [Symptoms or clues that were misleading]

---

### 7. Recommendations

#### Prevent Similar Issues
- [Changes to prevent this class of bug]

#### Improve Detection
- [Better monitoring, tests, or alerts]

#### Process Improvements
- [Development workflow changes]

---

### 8. Key Takeaways

Summarize 2-3 main lessons in memorable form:

1. **[Lesson Title]**: [One sentence insight]
2. **[Lesson Title]**: [One sentence insight]
3. **[Lesson Title]**: [One sentence insight]

---

### Appendix (Optional)

- Relevant logs or stack traces
- Related documentation links
- Follow-up tasks created
