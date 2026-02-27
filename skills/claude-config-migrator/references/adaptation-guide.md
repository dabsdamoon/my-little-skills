# Adaptation Guide

Per-element-type guidance on evaluating relevance, adapting elements for a target repo, and resolving conflicts.

---

## Decision Framework

For each source element, classify using this flowchart:

```
1. Does the target already have an equivalent? → Skip (conflict)
2. Is it specific to the source's domain/business? → Skip (irrelevant)
3. Is it tech-stack agnostic or matches target stack? → Copy as-is
4. Is it useful but references wrong paths/tools/stack? → Adapt and copy
5. Otherwise → Skip (irrelevant)
```

---

## Per-Element Adaptation Rules

### Settings (`settings.json`)

**When to copy as-is:**
- Generic tool permissions (e.g., allowing `Read`, `Glob`, `Grep`)
- Model preferences that aren't project-specific

**When to adapt:**
- `allowedTools` entries referencing project-specific commands (e.g., `Bash(npm run build)` → `Bash(cargo build)`)
- Permission rules tied to specific file paths

**When to skip:**
- Entries that only make sense for the source project's workflow

**Merge strategy:** Merge arrays (`allowedTools`, `deniedTools`) by union. For conflicting scalar values, prefer target's existing value.

---

### CLAUDE.md Files

**When to copy as-is:**
- Generic coding style sections (e.g., "use early returns", "prefer composition over inheritance")
- Communication preferences (e.g., "be concise", "don't add emojis")

**When to adapt:**
- Architecture descriptions → rewrite for target
- File path references → update to target structure
- Tech-stack-specific conventions → translate to target stack

**When to skip:**
- Project overview / business context sections
- Deployment-specific instructions
- Sections about source repo's specific tools or services

**Merge strategy:** Append transferable sections to existing CLAUDE.md under a clearly labeled heading. Never overwrite existing content. Use:
```markdown
## Migrated from [source-repo-name]
[transferred sections here]
```

---

### Rules (`.claude/rules/*.md`)

**When to copy as-is:**
- Language-agnostic practices: "write tests for all new code", "no console.log in production"
- Generic quality rules: error handling patterns, security practices
- Communication rules: "explain changes before making them"

**When to adapt:**
- Rules referencing specific linters/formatters → substitute target's equivalents
- Rules with path references → update paths
- Language-specific rules → translate idioms (e.g., "use `pytest`" → "use `jest`")

**When to skip:**
- Rules about source-specific frameworks or libraries not in target
- Rules about source-specific deployment pipelines

**Merge strategy:** Copy files directly. If a file with the same name exists in target, compare content — if semantically equivalent, skip; if complementary, rename with suffix (e.g., `testing-rules-migrated.md`).

---

### Skills (`.claude/skills/*/`)

**When to copy as-is:**
- Generic utility skills (PDF handling, spreadsheet processing, documentation)
- Skills whose scripts have no project-specific dependencies

**When to adapt:**
- Skills with hardcoded paths in scripts → update paths
- Skills referencing specific package managers → substitute target's
- Skills with tech-stack-specific references in SKILL.md → update references

**When to skip:**
- Skills tied to source's business domain (e.g., company-specific design system)
- Skills that depend on source-specific MCP servers or infrastructure

**Merge strategy:** Copy entire skill directory. If skill with same name exists in target, present both to user for manual decision — never auto-merge skills.

---

### Commands (`.claude/commands/*.md`)

**When to copy as-is:**
- Generic workflow commands (commit helpers, code review, PR creation)
- Commands that only use standard Claude Code tools

**When to adapt:**
- Commands referencing specific build tools → substitute target's
- Commands with hardcoded paths → update paths

**When to skip:**
- Commands for source-specific workflows (e.g., deploy to source's infrastructure)

**Merge strategy:** Copy files directly. If command with same name exists, compare and let user decide.

---

### Agents (`.claude/agents/*.md`)

**When to copy as-is:**
- Generic agents (code reviewer, test runner, documentation writer)

**When to adapt:**
- Agents referencing specific tools or APIs → update tool references
- Agents with tech-stack-specific instructions → translate

**When to skip:**
- Agents tied to source-specific services or infrastructure

**Merge strategy:** Copy files directly. If agent with same name exists, compare and let user decide.

---

### Hooks (`.claude/hooks/`)

**When to copy as-is:**
- Rarely — hooks almost always have project-specific paths

**When to adapt:**
- Replace source-specific tool invocations with target equivalents
- Update file paths and directory references
- Adjust environment variable names

**When to skip:**
- Hooks tied to source's CI/CD pipeline
- Hooks that invoke source-specific services

**Merge strategy:** Copy files. If same-named hook exists, present diff to user.

---

### MCP Configuration (`.mcp.json`)

**When to copy as-is:**
- Almost never — MCP configs reference local server paths and credentials

**When to adapt:**
- Server entries where the user wants the same MCP server in the target
- Update `command` paths, `args`, and `env` references

**When to skip:**
- Servers specific to source project's infrastructure
- Entries with credential/API key references (flag for manual setup)

**Merge strategy:** Merge `mcpServers` objects by key. If same server name exists in both, prefer target's configuration. New servers are added. Always flag `env` fields for manual credential review.

---

## Common Adaptation Patterns

### Path Replacement

| Source Pattern | Target Adaptation |
|---------------|-------------------|
| `src/components/` | Detect target's component directory |
| `npm run test` | Detect target's test command |
| `python -m pytest` | Match target's test runner |
| `.github/workflows/` | Keep if target uses GitHub Actions |

### Tech Stack Translation

| Source Stack | Target Stack | Adaptations Needed |
|-------------|-------------|-------------------|
| React | Vue | Component patterns, file extensions, imports |
| npm | yarn/pnpm | Command references in rules and hooks |
| Python | Node.js | Test runner, linter, formatter references |
| Jest | pytest | Test command references, assertion patterns |

### Naming Conflicts

When source and target have elements with the same filename:
1. Compare content for semantic equivalence
2. If equivalent → skip (already exists)
3. If complementary → merge content or rename with `-migrated` suffix
4. If contradictory → present both to user, let them choose

---

## Red Flags (Always Flag for Review)

- Any `env` field in MCP config → potential secrets
- Hooks that execute `rm`, `git push`, or other destructive commands
- Settings that disable security features (e.g., denying safety tools)
- Rules that contradict target's existing rules
- Skills with large binary assets (fonts, images) → confirm user wants to copy
