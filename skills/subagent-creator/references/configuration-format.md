# Subagent Configuration Format

## File Structure

Subagents are markdown files with YAML frontmatter stored in `.claude/agents/` within a repository.

```
.claude/
└── agents/
    ├── code-reviewer.md
    ├── test-writer.md
    └── doc-generator.md
```

## YAML Frontmatter

Required fields in the frontmatter:

```yaml
---
name: agent-name
description: When and why to use this agent. Be specific and action-oriented.
tools: Read, Grep, Glob  # Optional: restricts available tools
---
```

### Field Specifications

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, lowercase with hyphens |
| `description` | Yes | Activation criteria - when Claude should invoke this agent |
| `tools` | No | Comma-separated list of allowed tools (omit for all tools) |

### Tools Reference

Common tool combinations by agent type:

| Agent Type | Tools | Use Case |
|------------|-------|----------|
| Read-only | `Read, Grep, Glob` | Reviewers, analyzers |
| Research | `Read, Grep, Glob, WebFetch, WebSearch` | Documentation lookup |
| Code writer | `Read, Write, Edit, Bash, Glob, Grep` | Implementation agents |
| Full access | *(omit field)* | Orchestrators, complex tasks |

### Description Best Practices

The description is the primary trigger mechanism. Include:

1. **What** the agent does
2. **When** to invoke it (specific triggers)
3. **Scope** boundaries (what parts of codebase)

Examples:

```yaml
# Good - specific and actionable
description: Reviews TypeScript changes in src/api/. Use after modifying API endpoints, middleware, or request handlers.

# Bad - vague
description: Helps with code review.
```

## System Prompt Body

After the frontmatter, write markdown instructions:

```yaml
---
name: api-reviewer
description: Reviews API changes in src/api/. Use for PRs modifying routes or controllers.
tools: Read, Grep, Glob
---

# API Reviewer

You review API code changes for this repository.

## Repository Context
- API source: `src/api/`
- Route definitions: `src/api/routes/`
- Shared types: `src/types/`

## Review Guidelines
1. Check error handling patterns
2. Verify route naming conventions
3. Ensure request validation exists

## Output Format
Provide structured feedback with:
- Summary of changes reviewed
- Issues found (with file:line references)
- Suggestions for improvement
```

## Storage Locations

| Location | Scope | Priority |
|----------|-------|----------|
| `.claude/agents/` (project) | Current repository only | Higher (overrides global) |
| `~/.claude/agents/` (global) | All repositories | Lower |

Project-specific agents override global agents with the same name.
