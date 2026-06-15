---
name: update-notes
description: "Write concise project update notes, release notes, or changelog entries after code or documentation changes. Use when the user asks to summarize recent changes, document completed work, update UPDATE.md, CHANGELOG.md, or release notes, or create a project-facing change summary."
---

# Update Notes

Write short, concrete update notes for a project after implementation, refactoring, documentation, or operational changes.

## Workflow

1. Inspect changed work with `git status --short`, `git diff --stat`, and targeted `git diff` reads. If the directory is not a Git worktree, inspect the files the user names.
2. Locate the project notes target. Prefer an existing `docs/UPDATE.md`, `UPDATE.md`, `CHANGELOG.md`, or `RELEASE_NOTES.md`. If none exists, ask before creating a new notes file unless the user already specified a path.
3. Read the latest entries to match ordering, headings, tense, and level of detail.
4. Add one entry that covers only the current completed changes. Keep unrelated or speculative work out.
5. Verify the edited note for duplicated claims, stale dates, broken markdown, and paths that no longer exist.

## Entry Guidance

- Use today's date in `YYYY-MM-DD` unless the existing file uses another date format.
- Prefer newest-first when the file already follows that convention; otherwise preserve the existing order.
- Keep summaries concise: what changed, why it matters, and any behavior or migration impact.
- Use concrete file paths and feature names instead of broad claims.
- Skip sections that do not apply. Do not invent testing, migration, or deployment details.
- For the Houmy repository, prefer the project-specific `update-houmy-notes` skill when available.

## Suggested Format

When the target file has no established format, use:

```markdown
## YYYY-MM-DD: Short Title

### Summary
1-3 sentences describing the user-visible or operational effect.

### Changes
- `path/to/file`: Brief description of the meaningful change.

### Verification
- Command or manual check performed, if any.
```
