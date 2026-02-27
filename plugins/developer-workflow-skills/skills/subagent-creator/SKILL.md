---
name: subagent-creator
description: Creates repository-specific Claude Code subagents. Use when asked to create a subagent, add a custom agent, or build specialized automation for a codebase. Analyzes the repository structure, tech stack, and conventions before generating tailored subagent configurations.
---

# Subagent Creator

Create Claude Code subagents tailored to a specific repository's structure, conventions, and tech stack.

## Workflow Overview

```
1. Analyze Repository → 2. Gather Requirements → 3. Generate Subagent → 4. Validate & Save
```

## Step 1: Analyze Repository

Before creating any subagent, analyze the repository to ground the agent in actual context.

### Quick Analysis

Run these checks to understand the codebase:

1. **Directory structure**: Identify src/, tests/, docs/, config locations
2. **Tech stack**: Check package.json, pyproject.toml, Cargo.toml, go.mod
3. **Existing agents**: Check `.claude/agents/` for current subagents
4. **Conventions**: Read CLAUDE.md if present, check linting configs

### What to Extract

| Category | Information to Gather |
|----------|----------------------|
| Structure | Key directories, entry points, test locations |
| Tech stack | Languages, frameworks, package manager |
| Conventions | Naming style, error handling patterns, test patterns |
| Existing agents | Current agents and their scopes (avoid overlap) |

See [references/repo-analysis-checklist.md](references/repo-analysis-checklist.md) for detailed analysis guidance.

## Step 2: Gather Requirements

Ask the user:

1. **Purpose**: "What should this subagent do?"
2. **Scope**: "Which parts of the codebase should it focus on?"
3. **Agent type**: Present options based on purpose:
   - **Reviewer** (read-only): Code review, security analysis, style checking
   - **Writer** (read/write): Test generation, documentation, implementation
   - **Specialist** (focused): API work, database tasks, specific framework

## Step 3: Generate Subagent

### File Format

Create a markdown file with YAML frontmatter:

```yaml
---
name: {agent-name}
description: {specific trigger criteria including paths}
tools: {appropriate tool set}
---

# {Agent Title}

{Role description grounded in this repository}

## Repository Context
{Actual paths, patterns, and conventions from analysis}

## Guidelines
{Specific instructions for this agent's tasks}

## Output Format
{Expected response structure}
```

### Tool Selection

| Agent Type | Tools |
|------------|-------|
| Read-only (reviewers) | `Read, Grep, Glob` |
| Research | `Read, Grep, Glob, WebFetch, WebSearch` |
| Code writers | `Read, Write, Edit, Bash, Glob, Grep` |
| Full access | *(omit tools field)* |

### Description Guidelines

The description is the trigger mechanism. Include:
- **What** the agent does
- **When** to use it (specific paths, file types, scenarios)
- **Scope** boundaries

Example:
```yaml
description: Reviews Python API changes in src/api/. Use when PRs modify endpoints, middleware, or request handlers in the FastAPI backend.
```

See [references/configuration-format.md](references/configuration-format.md) for format details.
See [references/agent-type-examples.md](references/agent-type-examples.md) for templates.

## Step 4: Validate & Save

### Validation Checklist

Before saving, verify:

- [ ] **Single responsibility**: Agent has one clear purpose
- [ ] **Repository-grounded**: Includes actual paths from analysis
- [ ] **Specific description**: Trigger criteria are clear and actionable
- [ ] **Appropriate tools**: Minimum necessary permissions
- [ ] **No overlap**: Doesn't duplicate existing agents

See [references/best-practices.md](references/best-practices.md) for design patterns.

### Save Location

Save to `.claude/agents/{agent-name}.md` in the repository:

```bash
mkdir -p .claude/agents
# Write the subagent file
```

## Example: Complete Workflow

**User request**: "Create a subagent for reviewing my API code"

**Step 1 - Analysis findings**:
```
Repository: node-backend
Tech stack: TypeScript, Express, Prisma
Source: src/
API routes: src/routes/
Tests: tests/ (Jest)
Existing agents: none
Conventions: camelCase, async/await error handling
```

**Step 2 - Requirements gathered**:
- Purpose: Review API endpoint changes
- Scope: src/routes/, src/middleware/, src/controllers/
- Type: Reviewer (read-only)

**Step 3 - Generated subagent**:

```yaml
---
name: api-reviewer
description: Reviews API changes in src/routes/, src/middleware/, and src/controllers/. Use when PRs modify Express endpoints, middleware, or request handlers.
tools: Read, Grep, Glob
---

# API Reviewer

You review API code changes for node-backend.

## Repository Context
- Routes: `src/routes/` (Express routers)
- Middleware: `src/middleware/`
- Controllers: `src/controllers/`
- Tests: `tests/` (Jest, pattern: `*.test.ts`)
- Types: `src/types/`
- Database: Prisma ORM, schema at `prisma/schema.prisma`

## Review Checklist

### Must Pass
- [ ] Error handling uses try/catch with proper status codes
- [ ] Request validation exists for body/params
- [ ] New endpoints have corresponding tests
- [ ] No hardcoded secrets or credentials

### Should Pass
- [ ] Follows RESTful naming conventions
- [ ] Response types match TypeScript interfaces
- [ ] Middleware order is correct

## Output Format

## Review Summary
[1-2 sentence overview]

## Issues
- **[HIGH/MED/LOW]** `file:line` - [description]

## Suggestions
[Optional improvements]

## Verdict
[APPROVE / REQUEST_CHANGES]
```

**Step 4 - Saved to**: `.claude/agents/api-reviewer.md`

## References

- [Configuration Format](references/configuration-format.md) - YAML structure and field specifications
- [Best Practices](references/best-practices.md) - Design patterns and anti-patterns
- [Repository Analysis](references/repo-analysis-checklist.md) - What to check before creating agents
- [Agent Type Examples](references/agent-type-examples.md) - Templates for common agent types
