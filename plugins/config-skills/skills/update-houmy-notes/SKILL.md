---
name: update-houmy-notes
description: Write concise update notes to docs/UPDATE.md in the Houmy repository. Use when code changes are complete and need to be documented as release notes. Triggers on "update notes", "write update", "document changes", or after implementing features/fixes in the Houmy repo. IMPORTANT - this skill must be delegated to a sonnet-model Task subagent for cost efficiency.
---

# Update Houmy Notes

Append a new entry to `docs/UPDATE.md` in the Houmy repo. Run as a **sonnet-model subagent** to save cost.

## Workflow

1. Use `git diff` and `git status` to identify all changed files
2. Read the top of `docs/UPDATE.md` to see the latest entry format
3. Prepend a new entry after the `# Houmy RAG Chatbot - Update Notes` header
4. Follow the format below exactly

## Entry Format

```markdown
## YYYY-MM-DD: Short Feature Title

### Summary
1-3 sentences. What changed and why.

### Changes
| File | What changed |
|------|-------------|
| `path/to/file.py` | Brief semicolon-separated list of changes |

### Behavior
- **Scenario A**: what happens
- **Scenario B**: what happens

---
```

## Rules

- **Be concise** - each table row is one line; avoid paragraphs
- **Date** - use today's date (YYYY-MM-DD)
- **Newest first** - prepend after the H1 header, before existing entries
- **Omit optional sections** - skip Behavior/Migration/Usage if not needed
- **No duplication** - don't repeat info already in the Summary in the table
- **backtick paths** - wrap file paths and code identifiers in backticks

## Execution

Always delegate to a Task subagent with `model: "sonnet"`:

```
Task(
  subagent_type="general-purpose",
  model="sonnet",
  prompt="Read git diff for unstaged changes, read top of docs/UPDATE.md for format, then prepend a new update entry. Follow the update-houmy-notes skill format. <rules from SKILL.md>"
)
```
