# Subagent Best Practices

## Core Design Principles

### Single Responsibility

Each subagent should have one clear goal with defined:
- **Inputs**: What triggers the agent
- **Outputs**: What the agent produces
- **Boundaries**: What the agent does NOT do

Bad: "General code helper that reviews, writes tests, and updates docs"
Good: "Reviews TypeScript API changes for error handling patterns"

### Permission Hygiene

Restrict tools to minimum necessary:

```yaml
# Reviewer - read-only access
tools: Read, Grep, Glob

# Implementer - needs write access
tools: Read, Write, Edit, Bash, Glob, Grep

# Researcher - needs web access
tools: Read, Grep, Glob, WebFetch, WebSearch
```

Omitting `tools` grants all available tools - be deliberate about this.

### Repository-Grounded Context

Always include repo-specific information:

```markdown
## Repository Context
- Source code: `src/`
- Tests: `tests/` (pytest, files named `test_*.py`)
- Config: `pyproject.toml`, `.env.example`
- Key patterns: Repository uses dependency injection via `src/di/container.py`
```

## Prompt Structure Patterns

### Pattern 1: Role + Context + Guidelines

```markdown
# [Agent Name]

You are a [role] for [repository purpose].

## Repository Context
[Specific paths, patterns, conventions]

## Guidelines
[Numbered list of what to check/do]

## Output Format
[Expected structure of response]
```

### Pattern 2: Checklist-Based

```markdown
# [Agent Name]

Review changes against this checklist:

## Must Pass
- [ ] [Critical requirement 1]
- [ ] [Critical requirement 2]

## Should Pass
- [ ] [Important but not blocking]

## Nice to Have
- [ ] [Suggestions]
```

### Pattern 3: Decision Tree

```markdown
# [Agent Name]

## Decision Flow

1. If [condition A]:
   - Do [action A]
   - Check [specific files]

2. If [condition B]:
   - Do [action B]
   - Reference [pattern location]

3. Otherwise:
   - Default behavior
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Generic descriptions | Agent never triggers correctly | Include specific file paths and triggers |
| All tools enabled | Security risk, unfocused agent | Restrict to minimum needed tools |
| No repo context | Agent makes wrong assumptions | Include actual paths, conventions, tech stack |
| Overlapping agents | Confusion about which to use | Clear scope boundaries in descriptions |
| Too many responsibilities | Poor quality output | Split into focused agents |

## Orchestration Strategies

### Sequential Pipeline

For multi-step workflows, create separate agents that hand off:

```
spec-writer → architect-reviewer → implementer → test-writer
```

Each agent's description specifies when it activates in the pipeline.

### Parallel Specialists

For independent concerns, create agents that can run concurrently:

```
┌─ security-reviewer
│
├─ performance-reviewer
│
└─ style-reviewer
```

### Scope Isolation

When running parallel agents, ensure they operate on disjoint code areas to prevent conflicts:

```yaml
# Agent 1
description: Reviews frontend changes in src/components/

# Agent 2
description: Reviews backend changes in src/api/
```

## Human-in-the-Loop

### Approval Gates

Design agents to pause for human approval at critical points:

```markdown
## Output Format

Provide your analysis, then ask:
"Ready to proceed with implementation? (yes/no)"
```

### Visible Handoffs

Make agent transitions explicit:

```markdown
## Completion

When done, output:
"[agent-name] complete. Suggested next: [next-agent-name]"
```

## Iteration Workflow

1. **Create minimal agent** - Start with basic description and context
2. **Test on real tasks** - Use the agent on actual repository work
3. **Identify gaps** - Note where agent struggles or makes mistakes
4. **Refine prompt** - Add specific guidance for failure cases
5. **Repeat** - Continue until agent performs reliably
