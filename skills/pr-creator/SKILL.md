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

### Step 1: Gather Information

Before writing the PR, collect the following information:

1. **Branch information**: Source and target branches
2. **Git diff**: Run `git diff <target-branch>...HEAD` to see all changes
3. **Commit history**: Run `git log <target-branch>..HEAD --oneline` to see commits
4. **Changed files**: Run `git diff <target-branch>...HEAD --name-status` to list files
5. **Context**: Ask the user about the purpose/reason for the changes if not clear

### Step 2: Analyze Changes

For each changed file, understand:
- **What** changed (added, modified, deleted)
- **Why** it changed (bug fix, feature, refactor, etc.)
- **Impact** on other parts of the system

### Step 3: Write PR Documentation

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

- [ ] [Test case 1 - describe what to test]
- [ ] [Test case 2 - describe what to test]
- [ ] [Test case 3 - describe what to test]
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

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
- Be specific about what to test
- Include both automated and manual tests
- Cover edge cases and regression tests

## Keywords

PR, pull request, merge request, code review, git, documentation, changelog
