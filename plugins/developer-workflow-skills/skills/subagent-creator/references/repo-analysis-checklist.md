# Repository Analysis Checklist

Before creating a subagent, analyze the repository to ground the agent in actual codebase context.

## 1. Directory Structure

Identify key directories:

```bash
# Run to get structure overview
ls -la
find . -type d -maxdepth 2 | grep -v node_modules | grep -v .git | grep -v __pycache__
```

Common patterns to identify:

| Directory | Purpose |
|-----------|---------|
| `src/`, `lib/`, `app/` | Source code |
| `tests/`, `test/`, `__tests__/` | Test files |
| `docs/`, `documentation/` | Documentation |
| `scripts/`, `bin/` | Utility scripts |
| `config/`, `configs/` | Configuration |
| `public/`, `static/`, `assets/` | Static files |
| `.claude/agents/` | Existing subagents |

## 2. Tech Stack Detection

### Package Managers & Dependencies

| File | Stack Indicator |
|------|-----------------|
| `package.json` | Node.js/JavaScript/TypeScript |
| `pyproject.toml`, `requirements.txt`, `setup.py` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `pom.xml`, `build.gradle` | Java |

### Frameworks

Look in dependency files for:

| Framework | Files to Check |
|-----------|----------------|
| React | `package.json` → "react" |
| Next.js | `next.config.js`, "next" in deps |
| Express | "express" in deps |
| FastAPI | "fastapi" in deps |
| Django | "django" in deps, `manage.py` |
| Spring | `pom.xml` with spring dependencies |

### Build Tools

| Tool | Indicator |
|------|-----------|
| Webpack | `webpack.config.js` |
| Vite | `vite.config.js` |
| ESBuild | `esbuild` in deps |
| Make | `Makefile` |
| Just | `justfile` |

## 3. Coding Conventions

### From CLAUDE.md

If `.claude/CLAUDE.md` or `CLAUDE.md` exists, extract:
- Coding style preferences
- Naming conventions
- Architecture patterns
- Commit message format

### From Linting/Formatting Config

| File | Information |
|------|-------------|
| `.eslintrc.*` | JavaScript style rules |
| `.prettierrc` | Formatting preferences |
| `ruff.toml`, `.flake8` | Python style |
| `rustfmt.toml` | Rust formatting |
| `.editorconfig` | Editor settings |

### From Existing Code

Sample a few files to identify:
- Naming style (camelCase, snake_case, PascalCase)
- Comment style and documentation patterns
- Error handling patterns
- Import organization

## 4. Testing Setup

| Framework | Indicator Files |
|-----------|-----------------|
| Jest | `jest.config.js`, `*.test.js` |
| Pytest | `pytest.ini`, `conftest.py`, `test_*.py` |
| Vitest | `vitest.config.js` |
| Go test | `*_test.go` |
| RSpec | `spec/` directory, `*_spec.rb` |

Note test file patterns for inclusion in subagent context.

## 5. Existing Subagents

Check `.claude/agents/` for:
- What agents already exist
- Naming conventions used
- Scope boundaries already defined
- Gaps that new agent could fill

Avoid creating overlapping agents.

## 6. Key Files to Reference

Identify files the subagent may need to reference:

| Type | Examples |
|------|----------|
| Entry points | `main.py`, `index.ts`, `app.js` |
| Configuration | `config.yaml`, `.env.example` |
| Type definitions | `types.ts`, `models.py`, `schema.prisma` |
| API routes | `routes/`, `api/`, `endpoints/` |
| Database | `migrations/`, `schema.sql` |

## 7. Analysis Output Template

After analysis, summarize findings for use in subagent creation:

```markdown
## Repository Summary

**Name**: [repo-name]
**Purpose**: [brief description]
**Tech Stack**: [languages, frameworks]
**Package Manager**: [npm/pip/cargo/etc.]

## Key Paths
- Source: `[path]`
- Tests: `[path]` ([framework], pattern: `[pattern]`)
- Config: `[files]`
- Types/Models: `[path]`

## Conventions
- Naming: [style]
- Error handling: [pattern]
- Testing: [approach]

## Existing Agents
- [agent-1]: [scope]
- [agent-2]: [scope]

## Suggested Agent Opportunities
- [gap-1]: [potential agent]
- [gap-2]: [potential agent]
```
