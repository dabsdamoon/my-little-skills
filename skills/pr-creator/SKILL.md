---
name: pr-creator
description: Creates professional Pull Request (PR) documentation in markdown format. Use this skill when asked to create a PR, write PR notes, document code changes for review, or prepare merge request documentation. The skill analyzes git changes, understands the codebase context, and produces comprehensive PR documentation.
---

# PR Creator Skill

Creates comprehensive Pull Request documentation in markdown format, suitable for copying into GitHub/GitLab PR descriptions or saving as PR notes.

## When to Use This Skill

- Creating PR documentation for code changes
- Writing PR notes before submitting for review
- Documenting what changed and why
- Preparing merge request descriptions

## How to Create PR Documentation

### Step 1: Gather Information (Run in Parallel)

Before writing the PR, collect information by running these git commands **in parallel** (single message, multiple Bash tool calls for speed):

```bash
# Run ALL THREE in parallel (single message with 3 Bash tool calls)
git log <target-branch>..HEAD --oneline           # Commit history
git diff <target-branch>...HEAD --name-status     # Changed files list
git diff <target-branch>...HEAD --stat            # Change statistics
```

**After** reviewing the above, only run full diff for specific files if needed:
```bash
git diff <target-branch>...HEAD -- path/to/specific/file.ts
```

**Context**: Ask the user about the purpose/reason for the changes if not clear from commits

### Step 2: Blast Radius Analysis

Assess how far the changes ripple through the codebase. Run these **in parallel**:

```bash
# For each modified file, find how many other files depend on it
# Repeat for key changed files
grep -rn "from.*<changed-module>.*import\|require.*<changed-module>" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" .
grep -rn "<changed-function-or-class>" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" . | grep -v "def \|function \|class "
```

Classify each changed file:

| Blast Radius | Criteria | Review Urgency |
|---|---|---|
| **LOW** | Leaf file (no other files import it), test files, docs | Normal |
| **MEDIUM** | Imported by 2-5 files, component used in a few pages | Careful |
| **HIGH** | Imported by 6+ files, shared utility/hook/service, config files | Thorough |
| **CRITICAL** | Auth, DB schema, API contracts, env config, CI/CD | Requires sign-off |

Include the blast radius summary in the PR documentation (see template below).

### Step 3: Security Analysis

Scan the diff for common security concerns. Check for:

**Secrets & Credentials:**
```bash
# Search diff for potential secrets
git diff <target-branch>...HEAD | grep -iE "(password|secret|token|api_key|apikey|private_key|credential|auth_token)\\s*[=:]" | grep -v "\\.(md|txt|example):"
```

**OWASP Top 10 Checks (review the diff for):**

| Category | What to Look For |
|---|---|
| **Injection** | Raw SQL, unsanitized user input in queries, `eval()`, `exec()`, template literals in queries |
| **Broken Auth** | Hardcoded tokens, missing auth checks on new endpoints, session handling changes |
| **Sensitive Data** | Logging PII, exposing internal errors to clients, new env vars with secrets |
| **XSS** | `dangerouslySetInnerHTML`, unescaped user content, `innerHTML` assignment |
| **Insecure Dependencies** | New packages with known CVEs, pinned to vulnerable versions |
| **Misconfiguration** | CORS wildcards (`*`), debug mode in prod, permissive file permissions |
| **SSRF** | User-controlled URLs passed to `fetch`/`requests` without validation |

**Rate the overall security posture:**
- **CLEAR** — No security-relevant changes detected
- **NOTE** — Minor items worth mentioning (e.g., new env var, new dependency)
- **CONCERN** — Issues found that should be addressed before merge

Include findings in the PR documentation (see template below).

### Step 4: Analyze Changes

For each changed file, understand:
- **What** changed (added, modified, deleted)
- **Why** it changed (bug fix, feature, refactor, etc.)
- **Impact** on other parts of the system

### Step 5: Write PR Documentation

Generate a markdown document with the following sections:

---

## PR Documentation Template

```markdown
# PR: [Title - Brief description of the change]

**Branch:** `[source-branch]` → `[target-branch]`
**Date:** [YYYY-MM-DD]
**Total Files Changed:** [count] ([new] new, [modified] modified, [deleted] deleted)

## Summary

[2-4 sentences explaining:]
- What this PR does
- Why this change is needed
- High-level approach taken

**Key Features/Fixes:**
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

---

## Blast Radius

| File | Dependents | Radius | Notes |
|------|-----------|--------|-------|
| `path/to/shared-util.ts` | 12 files | **CRITICAL** | Used across all services |
| `path/to/component.tsx` | 3 files | MEDIUM | Used in 3 pages |
| `path/to/leaf-file.ts` | 0 files | LOW | No downstream dependents |

**Overall Blast Radius:** [LOW / MEDIUM / HIGH / CRITICAL]

---

## Security Analysis

**Rating:** [CLEAR / NOTE / CONCERN]

[If CLEAR:]
> No security-relevant changes detected.

[If NOTE or CONCERN, list findings:]

| Category | Finding | Severity | File |
|----------|---------|----------|------|
| [e.g., Sensitive Data] | [e.g., New env var `API_SECRET` added] | NOTE | `path/to/file` |
| [e.g., Injection] | [e.g., Raw user input in SQL query] | CONCERN | `path/to/file` |

[If CONCERN, add recommended actions:]
> **Action Required:** [Describe what should be fixed before merge]

---

## Major Changes

### 1. [Major Change Category 1]

**Files Changed:**
- `path/to/file1.ts`
- `path/to/file2.ts`

**Why:**
[Explain why this change was needed]

**Key Implementation:**
```[language]
// Key code snippet if helpful
```

---

### 2. [Major Change Category 2]

[Repeat the pattern above for each major change category]

---

## All Files Changed

### [Category 1] Files ([count] files)

| File | Change | Purpose |
|------|--------|---------|
| `path/to/file.ts` | Modified | [Brief description] |
| `path/to/new-file.ts` | **NEW** | [Brief description] |
| `path/to/deleted-file.ts` | ~~Deleted~~ | [Why removed] |

### [Category 2] Files ([count] files)

[Repeat table for each category]

---

## Environment Variables

[If new environment variables are needed]

```env
# [Category]
VARIABLE_NAME=description-or-example-value
ANOTHER_VARIABLE=value
```

[If no new environment variables:]
> No new environment variables required.

---

## Testing Checklist

- [x] [Test case already verified by integration/unit tests]
- [x] [Another test case covered by automated tests]
- [ ] [Test case requiring manual verification - describe steps]
- [ ] [Another manual check needed]

---

## Related PRs / Dependencies

[If this PR depends on or relates to other PRs]

- [Related PR title](link) - [relationship description]

[If none:]
> No related PRs.

---

## Screenshots / Demo

[If applicable, include screenshots or demo links]

---

## Notes for Reviewers

[Any special instructions or areas to focus on during review]
```

---

## Guidelines

### Blast Radius Section
- Run dependency grep for every file with non-trivial changes
- Always classify each changed file into LOW / MEDIUM / HIGH / CRITICAL
- Flag CRITICAL items prominently — these need reviewer attention
- State the overall blast radius clearly

### Security Analysis Section
- Always scan the diff for secrets and OWASP concerns
- Rate as CLEAR if nothing found — don't skip the section
- For CONCERN items, include specific file and line references
- Recommend concrete fixes, not vague warnings

### Summary Section
- Be concise but complete
- Focus on the "what" and "why"
- Use bullet points for key features

### Major Changes Section
- Group related changes together
- Explain the reasoning, not just the code
- Include code snippets only when they add clarity

### Files Changed Section
- Categorize files logically (by feature, by type, etc.)
- Use tables for readability
- Mark NEW and Deleted files clearly

### Environment Variables Section
- Only include if new variables are needed
- Provide example values or descriptions
- Group by category if multiple

### Testing Checklist Section
- **Checked `[x]`**: Items already verified by existing integration/unit tests (pre-verified)
- **Unchecked `[ ]`**: Items that require manual verification by the reviewer (e.g., UI appearance, deploy steps, browser testing)
- Be specific about what to test
- Cover edge cases and regression tests

---

## Quick Template (for simple PRs)

For small changes (< 5 files), use this minimal format instead of the full template:

```markdown
## Summary
[1-2 sentences explaining what and why]

## Changes
- [bullet point for each major change]

## Test plan
- [x] [item verified by automated tests]
- [ ] [item requiring manual verification]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## Creating the PR with GitHub CLI

**IMPORTANT:** Always use the full path `/usr/local/bin/gh` to avoid shell alias conflicts (e.g., `gh` may be aliased to git functions).

For faster PR creation, use `gh pr create` with HEREDOC directly (avoids creating intermediate files):

```bash
/usr/local/bin/gh pr create --base main --head feature-branch --title "feat: Brief title" --body "$(cat <<'EOF'
## Summary
[1-2 sentences]

## Changes
- [bullet points]

## Test plan
- [ ] [verification steps]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**For longer PRs**, write to a temp file first then use `--body-file`:
```bash
# Write PR body to temp file
# Then create PR
/usr/local/bin/gh pr create --base main --head feature-branch --title "feat: Title" --body-file /tmp/pr-body.md
```

---

## Performance Tips

1. **Parallel git commands**: Always run `git log`, `git diff --name-status`, and `git diff --stat` in parallel (single message with multiple Bash calls)
2. **Use HEREDOC**: Avoid intermediate files for short PRs with `--body "$(cat <<'EOF' ... EOF)"`
3. **Stat before diff**: Use `--stat` first to see scope, only full diff specific files if needed
4. **Minimal first**: Start with quick template, add detail only if the PR is complex
5. **Skip optional sections**: Omit Screenshots/Demo, Related PRs, Environment Variables if not applicable
6. **Don't over-document**: A clear summary + changes list is often sufficient

## Keywords

PR, pull request, merge request, code review, git, documentation, changelog
