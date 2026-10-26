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
# Reviewer - reads code, runs git diff and tests, never edits
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit

# Implementer - needs write access
tools: Read, Write, Edit, Bash, Glob, Grep

# Researcher - needs web access
tools: Read, Grep, Glob, WebFetch, WebSearch
```

Omitting `tools` grants every tool available to subagents - be deliberate about this.

A reviewer without Bash can't run `git diff` or the tests, so it reviews blind. With Bash it can also change files, so:

- Say "Do not modify files; use Bash only for git and test commands" in the prompt.
- For hard enforcement, add a `PreToolUse` hook on Bash that rejects write commands (see [configuration-format.md](configuration-format.md#hooks)).
- Don't add `memory` to a read-only reviewer: it enables Write and Edit automatically.

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
| Read-only reviewer without Bash | Can't run `git diff` or tests | `tools: Read, Grep, Glob, Bash` plus `disallowedTools: Write, Edit` |
| No repo context | Agent makes wrong assumptions | Include actual paths, conventions, tech stack |
| Overlapping agents | Confusion about which to use | Check the roster first; clear scope boundaries in descriptions |
| Too many responsibilities | Poor quality output | Split into focused agents |
| Prompt asks the user a question | Subagents have no `AskUserQuestion` tool | Return the question to the main thread |
| Misspelled field (`max_turns`, `disallowed-tools`) | Silently ignored | Use the exact camelCase names; run the unknown-key check in SKILL.md Step 6 |

## Orchestration Strategies

### Sequential Pipeline

For multi-step workflows, create separate agents that hand off:

```
spec-writer → architect-reviewer → implementer → test-writer
```

Each agent's description specifies when it activates in the pipeline. The main conversation does the chaining: each subagent returns its result, and Claude passes the relevant context to the next one.

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

Writers that edit code in parallel can still conflict. Give them `isolation: worktree` so each works in its own temporary git worktree (branched from the default branch, not the current `HEAD`).

## Return to the Main Thread for Decisions

A subagent can't pause and ask the user. Claude Code removes `AskUserQuestion` from every subagent, and a subagent sees only its delegation message, not the conversation. A prompt that says "ask the user before proceeding" leaves the agent to guess or stall.

Design the agent to finish its turn and hand the decision back instead:

```markdown
## When You Need a Decision

If the next step depends on something only the user can decide (a breaking
change, a destructive migration, two valid designs), stop. Do not guess.
Return:
- What you found so far
- The decision needed, with the options and their trade-offs
- What you will do for each option
```

The main conversation then asks the user, and Claude can resume the same subagent with the answer (it keeps its full history when resumed). For risky actions the agent should never take on its own, remove the tool instead of relying on the prompt.

Tool permission prompts are different: those still reach the user. A background subagent's prompts surface in the main session, named after the subagent.

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
