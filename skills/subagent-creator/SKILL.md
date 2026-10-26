---
name: subagent-creator
description: Creates Claude Code subagents (.claude/agents/*.md) and matching Codex custom agents (.codex/agents/*.toml) grounded in the current repository. Use when asked to create, add, or design a subagent, custom agent, or specialized agent such as a reviewer, test runner, or researcher with limited tools. Checks the existing agent roster for duplicates before writing.
---

# Subagent Creator

Create subagents tailored to a repository's structure, conventions, and tech stack. Output a Claude Code subagent file, plus an equivalent Codex custom agent when the user works in Codex.

Every field, value, location, and precedence rule in this skill comes from the official docs listed under [Sources](#sources). Do not invent fields: Claude Code silently ignores frontmatter keys it does not recognize.

## Workflow Overview

```
1. Check roster → 2. Analyze repo → 3. Gather requirements → 4. Choose fields → 5. Write file(s) → 6. Validate & test
```

## Step 1: Check the Existing Agent Roster

Before designing anything, list the agents the user already has. Claude routes work by `description`, so two agents with overlapping scopes make delegation unpredictable, and two agents with the same `name` shadow each other.

Run these read-only commands from the repository:

```bash
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
{
  # Project agents (Claude Code scans every .claude/agents/ from cwd up to the repo root, recursively)
  find "$root" -path '*/node_modules' -prune -o -path '*/.claude/agents/*' -name '*.md' -print
  # User agents
  find ~/.claude/agents -name '*.md' 2>/dev/null
  # Plugin agents: every installed plugin's agents/ directory
  claude plugin list --json 2>/dev/null | jq -r '.[] | .readFromFolder // .installPath' |
    while IFS= read -r p; do find "$p/agents" -name '*.md' 2>/dev/null; done
} | while IFS= read -r f; do
  awk 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit}
       /^(name|description):/ {print FILENAME ": " substr($0, 1, 160)}' "$f"
done

# Codex custom agents (personal and project)
find ~/.codex/agents "$root/.codex/agents" -name '*.toml' \
  -exec grep -HE '^(name|description)[[:space:]]*=' {} + 2>/dev/null
```

A `description: |` line means a multi-line description; open that file to read it.

Also compare against:

- **Agents the current session can delegate to**: the Agent tool lists them, including plugin agents under scoped names such as `my-plugin:code-reviewer`.
- **Built-in agents**: Claude Code ships `Explore`, `Plan`, `general-purpose`, `claude`, `statusline-setup`, and `claude-code-guide`. Codex ships `default`, `worker`, and `explorer`.
- **Managed agents**: organizations can deploy agents in `.claude/agents/` inside the managed settings directory. They take precedence over every other scope.

Plugins with a manifest `agents` key load the files it lists instead of scanning `agents/`; check `.claude-plugin/plugin.json` when a plugin's agents look missing.

### Act on what you find

| Finding | Action |
|---------|--------|
| Same `name` in another location | One shadows the other (managed > `--agents` > project > user > plugin). Pick a different name or edit the existing agent |
| Same `name` twice under one `.claude/agents/` tree | Only one loads, chosen by filesystem order. `/doctor` reports these |
| A user or project agent named like a built-in (`Explore`) | It replaces the built-in. Do this only on purpose |
| Similar description or scope, any location | Show the user the overlap. Offer to extend or narrow the existing agent instead of adding a new one |
| Plugin agent with similar scope (e.g. `pr-review-toolkit:code-reviewer`) | It registers under a scoped name, but its description still competes for delegation. Make the new description clearly narrower |

Report the roster and any overlap to the user before writing a file.

## Step 2: Analyze the Repository

Ground the agent in real context:

1. **Directory structure**: src/, tests/, docs/, config locations
2. **Tech stack**: package.json, pyproject.toml, Cargo.toml, go.mod
3. **Test command**: how tests run (`npm test`, `pytest`, `go test ./...`), so the agent prompt can name it
4. **Conventions**: CLAUDE.md, AGENTS.md, linting configs
5. **Codex usage**: `AGENTS.md`, a `.codex/` directory, or the user saying they use Codex

| Category | Information to Gather |
|----------|----------------------|
| Structure | Key directories, entry points, test locations |
| Tech stack | Languages, frameworks, package manager |
| Conventions | Naming style, error handling patterns, test patterns |
| Existing agents | Roster from Step 1 and each agent's scope |

See [references/repo-analysis-checklist.md](references/repo-analysis-checklist.md) for detailed analysis guidance.

## Step 3: Gather Requirements

Ask the user:

1. **Purpose**: "What should this subagent do?"
2. **Scope**: "Which parts of the codebase should it focus on?"
3. **Agent type**:
   - **Reviewer**: reads code, runs `git diff` and tests, never edits
   - **Writer**: tests, documentation, implementation
   - **Specialist**: API, database, or framework-specific work
4. **Target**: Claude Code, Codex, or both
5. **Location**: this project (`.claude/agents/`, shared via version control) or every project (`~/.claude/agents/`)

Subagents cannot ask the user questions: Claude Code removes `AskUserQuestion` from every subagent. If the job involves decisions only the user can make, design the agent to stop and return the options to the main conversation. See [references/best-practices.md](references/best-practices.md#return-to-the-main-thread-for-decisions).

## Step 4: Choose Frontmatter Fields

Only `name` and `description` are required. Add other fields only when they change behavior the user needs.

### Tool Selection

| Agent Type | Frontmatter |
|------------|-------------|
| Reviewer (reads, runs `git diff` and tests) | `tools: Read, Grep, Glob, Bash` and `disallowedTools: Write, Edit` |
| Researcher | `tools: Read, Grep, Glob, WebFetch, WebSearch` |
| Writer | `tools: Read, Write, Edit, Bash, Glob, Grep` |
| Full access | Omit `tools` (inherits every tool available to subagents) |

- `tools` is an allowlist and `disallowedTools` is a denylist. When both are set, `disallowedTools` is applied first and a tool listed in both is removed, so the reviewer's denylist keeps Write and Edit out even if someone later widens `tools`.
- Bash can still change files. A reviewer's read-only promise lives in its prompt. For hard enforcement, add a `PreToolUse` hook on Bash; see [references/configuration-format.md](references/configuration-format.md#hooks).
- Omit `Agent` from `tools` to keep the subagent from spawning its own subagents.

### Other fields worth deciding

| Field | Use it when |
|-------|-------------|
| `model` | The job needs a specific tier: `haiku` for cheap high-volume work, `inherit` to match the main conversation. Omit to follow the default order |
| `effort` | The job needs more or less reasoning than the session: `low`, `medium`, `high`, `xhigh`, `max` (levels depend on the model) |
| `permissionMode` | The agent must run unattended (`dontAsk`) or auto-accept edits (`acceptEdits`). Overridden when the main conversation is in `bypassPermissions`, `acceptEdits`, auto, or `plan` mode; ignored for plugin agents |
| `isolation: worktree` | A writer may run in parallel with other writers. It branches from the default branch, so do not use it for reviewers of uncommitted work |
| `maxTurns` | You want a hard cap; output is returned marked partial and can be resumed |
| `memory` | The agent should learn across sessions. It auto-enables Read, Write, and Edit, so avoid it on read-only reviewers |

See [references/configuration-format.md](references/configuration-format.md) for every field, accepted values, and precedence rules.

## Step 5: Write the File

### Claude Code subagent

```markdown
---
name: {agent-name}
description: {What it does}. Use when {specific paths, file types, scenarios}.
tools: {allowlist}
---

# {Agent Title}

{Role description grounded in this repository}

## Repository Context
{Actual paths, patterns, test command, conventions from analysis}

## Guidelines
{Specific instructions for this agent's tasks}

## When You Need a Decision
Stop and return the open question with the options you see. Do not guess.

## Output Format
{Expected response structure}
```

The description is the trigger. Include **what** the agent does, **when** to use it (paths, file types, scenarios), and **scope** boundaries. Add "use proactively" to encourage automatic delegation. Keep it short: Claude Code warns when all subagent descriptions together pass 15,000 tokens.

```yaml
description: Reviews Python API changes in src/api/. Use when PRs modify endpoints, middleware, or request handlers in the FastAPI backend.
```

### Codex custom agent

When the user works in Codex, also write `.codex/agents/{agent-name}.toml` (project) or `~/.codex/agents/{agent-name}.toml` (personal) with `name`, `description`, and `developer_instructions`. Codex agent files have no per-tool allowlist and cannot override sandbox mode, approval policy, or MCP servers; they inherit those from the parent session. See [references/codex-custom-agents.md](references/codex-custom-agents.md) for the schema and field mapping.

See [references/agent-type-examples.md](references/agent-type-examples.md) for templates.

## Step 6: Validate, Save & Test

### Validation Checklist

- [ ] **No duplicates**: Roster from Step 1 has no same-name or same-scope agent the user didn't approve
- [ ] **Single responsibility**: One clear purpose
- [ ] **Repository-grounded**: Real paths, test command, conventions
- [ ] **Specific description**: Trigger criteria are concrete
- [ ] **Minimum tools**: Reviewers have `disallowedTools: Write, Edit`
- [ ] **Decisions return**: The prompt tells the agent to report open questions instead of asking
- [ ] **Valid fields only**: Every key appears in the field table, spelled in camelCase

### Save and check

```bash
mkdir -p .claude/agents
# Write .claude/agents/{agent-name}.md
claude plugin validate .claude/agents   # catches frontmatter that doesn't parse

# Unrecognized keys are silently ignored and validate doesn't flag them; this prints any
awk 'NR==1{next} /^---$/{exit} /^[A-Za-z]/{sub(/:.*/,""); print}' .claude/agents/{agent-name}.md |
  grep -vxE 'name|description|tools|disallowedTools|model|permissionMode|maxTurns|autoCompactWindow|skills|mcpServers|hooks|memory|background|omitClaudeMd|effort|isolation|color|initialPrompt|experimental'
```

- Claude Code picks up edits to existing `agents` directories within seconds. If `.claude/agents/` or `~/.claude/agents/` did not exist when the session started, restart Claude Code.
- Test with `@"{agent-name} (agent)"` or `@agent-{agent-name}` followed by a realistic task.
- For Codex files, check the TOML parses: `python3 -c 'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' .codex/agents/{agent-name}.toml`

## Example: Complete Workflow

**User request**: "Create a subagent for reviewing my API code"

**Step 1 - Roster**: no project or user agents; `pr-review-toolkit:code-reviewer` installed (general review). Told the user the new agent will be narrower: API routes only.

**Step 2 - Analysis**:
```
Repository: node-backend
Tech stack: TypeScript, Express, Prisma
API routes: src/routes/   Tests: tests/ (Jest, npx jest)
Conventions: camelCase, async/await error handling
Codex: not used
```

**Step 3 - Requirements**: review endpoint changes in src/routes/, src/middleware/, src/controllers/; reviewer; this project only.

**Step 5 - Generated subagent**:

```markdown
---
name: api-reviewer
description: Reviews API changes in src/routes/, src/middleware/, and src/controllers/. Use when PRs modify Express endpoints, middleware, or request handlers.
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
---

# API Reviewer

You review API code changes for node-backend. Do not modify files. Use Bash only for git and test commands.

## Repository Context
- Routes: `src/routes/` (Express routers)
- Middleware: `src/middleware/`
- Controllers: `src/controllers/`
- Tests: `tests/` (Jest, pattern: `*.test.ts`, run with `npx jest`)
- Database: Prisma ORM, schema at `prisma/schema.prisma`

## Process
1. Run `git diff main...HEAD -- src/routes src/middleware src/controllers` to see the changes
2. Read each changed file and its tests
3. Run `npx jest` for the affected test files

## Review Checklist

### Must Pass
- [ ] Error handling uses try/catch with proper status codes
- [ ] Request validation exists for body/params
- [ ] New endpoints have corresponding tests, and they pass
- [ ] No hardcoded secrets or credentials

### Should Pass
- [ ] Follows RESTful naming conventions
- [ ] Response types match TypeScript interfaces
- [ ] Middleware order is correct

## When You Need a Decision
If a finding depends on intent you can't infer (e.g. a breaking change to a public route), list it under Open Questions instead of guessing.

## Output Format

## Review Summary
[1-2 sentence overview]

## Issues
- **[HIGH/MED/LOW]** `file:line` - [description]

## Open Questions
[Decisions for the user, with options]

## Verdict
[APPROVE / REQUEST_CHANGES]
```

**Step 6 - Saved to**: `.claude/agents/api-reviewer.md`, validated with `claude plugin validate .claude/agents`.

## References

- [Configuration Format](references/configuration-format.md) - Every Claude Code frontmatter field, scopes, and precedence
- [Codex Custom Agents](references/codex-custom-agents.md) - TOML schema and mapping from Claude Code fields
- [Best Practices](references/best-practices.md) - Design patterns, returning decisions, anti-patterns
- [Repository Analysis](references/repo-analysis-checklist.md) - What to check before creating agents
- [Agent Type Examples](references/agent-type-examples.md) - Templates for common agent types

## Sources

Checked 2026-10-26 against Claude Code 2.1.310. None of these pages shows a last-updated date.

- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code plugin agents and CLI: https://code.claude.com/docs/en/plugins/components, https://code.claude.com/docs/en/plugins/cli-reference
- Codex subagents and custom agents: https://learn.chatgpt.com/docs/agent-configuration/subagents

Re-check these pages before relying on a field the docs mark with a minimum version, and when the user's Claude Code or Codex version differs.
