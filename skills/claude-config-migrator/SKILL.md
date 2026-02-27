---
name: claude-config-migrator
description: >
  Migrate Claude Code configuration between repositories. Use this skill when a user wants to
  transfer, copy, or migrate Claude Code config (rules, skills, commands, agents, hooks, settings,
  CLAUDE.md, MCP config) from one repository to another. Triggers on requests like "migrate my
  Claude config", "copy skills from repo X to repo Y", "transfer Claude setup between projects",
  "import Claude rules from another repo", or "set up this repo with my Claude config from
  another project". Handles discovery, relevance analysis, adaptation, and conflict resolution.
---

# Claude Config Migrator

Migrate Claude Code configuration elements (rules, skills, commands, agents, hooks, settings, CLAUDE.md, MCP config) from a source repository to a target repository with intelligent relevance analysis and conflict resolution.

## Workflow

Follow these 7 steps in order. Do not skip the user approval gate in Step 5.

---

### Step 1: Validate Inputs

Collect source and target repository paths. Both must be local filesystem directories.

- If the user didn't provide both paths, ask for them
- Verify the source has at least some Claude Code config by checking for:
  - `.claude/` directory
  - `CLAUDE.md` at root
  - `.mcp.json` at root
- If none exist, inform the user the source has no Claude Code config to migrate
- Verify the target directory exists

---

### Step 2: Scan Source Repository

Run the scanner script to produce a structured JSON inventory:

```bash
python skills/claude-config-migrator/scripts/scan_claude_config.py <source-path> --pretty
```

The scanner:
- Discovers all Claude Code config elements (settings, CLAUDE.md, rules, skills, commands, agents, hooks, MCP config)
- Automatically excludes `.local` files (private/personal — never migrate these)
- Outputs JSON with `summary` (counts by type) and `elements` array

Present the summary to the user:
```
Found N elements in source repo:
- X rules
- Y skills
- Z commands
...
```

If no elements found, stop and inform the user.

---

### Step 3: Analyze Target Repository

Examine the target repository to understand its context. Gather:

1. **Tech stack** — Check for `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Gemfile`, etc.
2. **Project structure** — Key directories (`src/`, `lib/`, `tests/`, `app/`), entry points
3. **Existing Claude Code config** — Run the scanner on the target too, to detect conflicts:
   ```bash
   python skills/claude-config-migrator/scripts/scan_claude_config.py <target-path> --pretty
   ```
4. **Conventions** — Linting config (`.eslintrc`, `ruff.toml`, `.prettierrc`), CI setup (`.github/workflows/`), coding style indicators

This context is essential for accurate classification in Step 4.

---

### Step 4: Classify Each Source Element

For every element from Step 2, classify it into one of four categories based on your understanding of both repositories:

| Category | Criteria | Action |
|----------|----------|--------|
| **Copy as-is** | Generic/universal, directly useful in target | Copy without modification |
| **Adapt and copy** | Useful but needs path, tech-stack, or tool modifications | Copy with documented changes |
| **Skip (irrelevant)** | Specific to source repo's domain, tech stack, or business | Do not copy |
| **Skip (conflict)** | Target already has an equivalent element | Do not copy |

**Classification guidance:**
- Read [config-element-catalog.md](references/config-element-catalog.md) for portability characteristics of each element type
- Read [adaptation-guide.md](references/adaptation-guide.md) for detailed per-element-type decision rules
- Rules and commands tend to be highly portable
- Skills vary — evaluate each individually
- CLAUDE.md sections should be evaluated independently (some sections transfer, others don't)
- MCP config is rarely portable as-is — flag credentials
- Hooks almost always need adaptation

For "Adapt and copy" elements, note the specific modifications needed.

---

### Step 5: Present Migration Plan to User

**This is a mandatory approval gate. Do not proceed without user confirmation.**

Present a structured migration plan grouped by classification:

```markdown
## Migration Plan: [source-repo] → [target-repo]

### Will Copy As-Is (N elements)
| # | Type | Path | Notes |
|---|------|------|-------|
| 1 | rule | .claude/rules/testing.md | Generic testing rules |
| 2 | command | .claude/commands/review.md | Standard review workflow |

### Will Adapt and Copy (N elements)
| # | Type | Path | Modifications |
|---|------|------|---------------|
| 3 | rule | .claude/rules/build.md | Replace `npm` → `yarn` |
| 4 | skill | .claude/skills/pdf/ | Update script paths |

### Will Skip — Irrelevant (N elements)
| # | Type | Path | Reason |
|---|------|------|--------|
| 5 | skill | .claude/skills/company-design/ | Source-specific domain |

### Will Skip — Conflict (N elements)
| # | Type | Path | Existing Target Element |
|---|------|------|------------------------|
| 6 | rule | .claude/rules/style.md | Target has equivalent |
```

Ask the user to:
- **Approve** the plan as-is
- **Exclude** specific items by number
- **Override** any classification (e.g., "copy #5 as-is" or "skip #3")

Wait for explicit confirmation before proceeding.

---

### Step 6: Execute Migration

For each approved element, execute the migration:

**Directory setup:**
- Create `.claude/` and subdirectories in target as needed (`rules/`, `skills/`, `commands/`, `agents/`, `hooks/`)

**Copy as-is elements:**
- Copy files directly from source to target, preserving relative paths

**Adapt and copy elements:**
- Copy the file, then apply the documented modifications
- For each adaptation, leave a comment or note about what was changed

**Merge rules (never overwrite):**

- **CLAUDE.md**: Append migrated sections under a `## Migrated from [source-repo]` heading. Never overwrite existing content.
- **settings.json**: Merge `allowedTools` and `deniedTools` arrays by union. For conflicting scalar values, keep target's value.
- **.mcp.json**: Merge `mcpServers` by key. Keep target's existing servers. Add new servers. Flag `env` fields for manual credential setup.
- **Same-name files** (rules, commands, agents): Compare content. If semantically equivalent, skip. If different, rename migrated file with `-migrated` suffix.

**Whole-skill copying:**
- When a skill is approved for migration, copy the entire skill directory tree (SKILL.md, scripts/, references/, assets/, etc.)
- Preserve internal directory structure exactly

---

### Step 7: Post-Migration Summary

Present a summary of everything that was done:

```markdown
## Migration Complete

### Files Created
- .claude/rules/testing.md
- .claude/rules/build.md (adapted: npm → yarn)
- .claude/skills/pdf/ (5 files)

### Files Merged
- CLAUDE.md (appended 2 sections)
- .claude/settings.json (added 3 allowed tools)

### Requires Manual Review
- .mcp.json: Notion server added — set up API credentials
- .claude/hooks/pre-commit.sh: Verify paths match target project

### Skipped (N elements)
[list with reasons]
```

**Always remind the user:**
- Review adapted files for correctness
- Set up credentials for any migrated MCP configs
- Test hooks in the target environment
- Review merged CLAUDE.md sections for relevance

---

## Edge Cases

- **Source and target are the same repo**: Warn the user and abort
- **Target has no `.claude/` directory**: Create it from scratch — this is a clean migration
- **Source has skills that reference MCP servers**: Flag the dependency — the MCP config may also need migration
- **Binary files in skills** (fonts, images): Copy as-is but note the size impact
- **Large skills** (>1MB total): Warn the user about size before copying
- **Nested CLAUDE.md files**: Only migrate root-level and `.claude/` level — subdirectory CLAUDE.md files are too context-specific
