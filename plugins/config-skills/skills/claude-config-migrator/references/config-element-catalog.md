# Claude Code Configuration Element Catalog

Complete reference of every Claude Code configuration element type, their locations, formats, and portability characteristics.

---

## Element Types

### 1. Settings (`settings`)

| Property | Value |
|----------|-------|
| **Location** | `.claude/settings.json` |
| **Private variant** | `.claude/settings.local.json` (never migrate) |
| **Format** | JSON object |
| **Contents** | Project-level Claude Code settings: allowed/denied tools, model preferences, permission rules, trusted commands |
| **Portability** | **Medium** — tool permissions may reference project-specific commands; model preferences are universal |

**Key fields:**
- `allowedTools` — array of tool patterns permitted without confirmation
- `deniedTools` — array of tool patterns always blocked
- `permissions` — granular permission rules for specific tools/actions
- `trustPromptTools` — boolean for trusting tool outputs

---

### 2. CLAUDE.md Files (`claude_md`)

| Property | Value |
|----------|-------|
| **Locations** | Root `CLAUDE.md`, `.claude/CLAUDE.md` |
| **Private variants** | `CLAUDE.local.md`, `.claude/CLAUDE.local.md` (never migrate) |
| **Format** | Markdown (free-form) |
| **Contents** | Project instructions, coding conventions, architecture notes, workflow preferences |
| **Portability** | **Low-Medium** — heavily project-specific; some sections (coding style, PR conventions) may transfer |

**Common sections:**
- Project overview and architecture
- Coding conventions and style rules
- Testing and CI requirements
- Dependency management preferences
- File organization patterns
- Communication preferences for Claude

---

### 3. Rules (`rule`)

| Property | Value |
|----------|-------|
| **Location** | `.claude/rules/*.md` |
| **Format** | Markdown files, one per rule |
| **Contents** | Individual behavioral rules or instructions that Claude should follow |
| **Portability** | **High** — most rules are generic coding practices; some reference specific paths or tools |

**Examples:**
- Code review guidelines
- Error handling patterns
- Naming conventions
- Security practices
- Testing requirements

---

### 4. Skills (`skill`)

| Property | Value |
|----------|-------|
| **Location** | `.claude/skills/<skill-name>/` |
| **Required file** | `SKILL.md` with YAML frontmatter (`name`, `description`) |
| **Supporting files** | `scripts/`, `references/`, `assets/`, `tests/` |
| **Format** | Directory containing SKILL.md + supporting resources |
| **Contents** | Specialized capabilities: workflows, scripts, domain knowledge |
| **Portability** | **Varies** — generic skills (PDF, testing) are highly portable; domain-specific skills (company design) are not |

**Structure:**
```
skill-name/
├── SKILL.md              # Required: instructions + YAML frontmatter
├── scripts/              # Optional: executable Python/Bash scripts
├── references/           # Optional: documentation, schemas, guides
├── assets/               # Optional: templates, fonts, images
└── tests/                # Optional: test files
```

**Migration note:** Skills must be copied as whole directories to preserve internal references between SKILL.md and supporting files.

---

### 5. Commands (`command`)

| Property | Value |
|----------|-------|
| **Location** | `.claude/commands/*.md` |
| **Format** | Markdown files defining slash commands |
| **Contents** | Custom user-invocable commands (e.g., `/commit`, `/review-pr`) |
| **Portability** | **Medium-High** — most commands are generic workflows; some reference project-specific paths or tools |

**Frontmatter fields:**
- `name` — command name (used as `/name`)
- `description` — when/how to use the command
- Parameters and argument definitions

---

### 6. Agents (`agent`)

| Property | Value |
|----------|-------|
| **Location** | `.claude/agents/*.md` |
| **Format** | Markdown files defining specialized subagents |
| **Contents** | Agent configurations with specialized behaviors, tool access, and workflow definitions |
| **Portability** | **Medium** — generic agents (code review, testing) are portable; agents referencing specific APIs/services are project-specific |

---

### 7. Hooks (`hook`)

| Property | Value |
|----------|-------|
| **Location** | `.claude/hooks/` (files and subdirectories) |
| **Format** | Shell scripts, Python scripts, or other executables |
| **Contents** | Event-driven scripts triggered by Claude Code actions (pre/post tool execution, startup, etc.) |
| **Portability** | **Low-Medium** — often reference project-specific paths, tools, or CI systems |

**Common hooks:**
- Pre-commit validation
- Post-tool-execution logging
- Startup environment checks
- Custom notification triggers

---

### 8. MCP Configuration (`mcp_config`)

| Property | Value |
|----------|-------|
| **Location** | Root `.mcp.json` |
| **Format** | JSON object |
| **Contents** | Model Context Protocol server configurations — external tool integrations |
| **Portability** | **Low** — references specific server paths, credentials, API keys, and local infrastructure |

**Key fields:**
- `mcpServers` — map of server name to configuration
  - `command` — executable path
  - `args` — command arguments
  - `env` — environment variables (may contain secrets)

**Migration warning:** MCP configs frequently contain credential references (`env` fields). These should never be copied blindly — flag for manual credential setup.

---

## Portability Summary

| Element Type | Portability | Typical Action |
|-------------|-------------|----------------|
| Rules | High | Copy as-is |
| Commands | Medium-High | Copy as-is or minor adaptation |
| Skills | Varies | Copy whole directory; evaluate per-skill |
| Settings | Medium | Merge selectively |
| Agents | Medium | Adapt tool/path references |
| CLAUDE.md | Low-Medium | Extract transferable sections only |
| Hooks | Low-Medium | Adapt paths and tool references |
| MCP Config | Low | Adapt; flag credentials for manual setup |

---

## Privacy Rules

The following files are **always excluded** from migration:
- `.claude/settings.local.json` — personal tool permissions
- `CLAUDE.local.md` — personal project instructions
- `.claude/CLAUDE.local.md` — personal project instructions

These contain user-specific preferences, local paths, and potentially sensitive information.
