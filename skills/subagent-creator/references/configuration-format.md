# Subagent Configuration Format (Claude Code)

Everything here comes from the Claude Code subagents docs listed under Sources in SKILL.md. For Codex, see [codex-custom-agents.md](codex-custom-agents.md).

## File Structure

A subagent is a Markdown file: YAML frontmatter between `---` markers, then the system prompt as Markdown.

```
.claude/
└── agents/
    ├── code-reviewer.md
    └── review/
        └── security.md
```

- `.claude/agents/` and `~/.claude/agents/` are scanned recursively. Subfolders are only for organization: identity comes from the `name` field, and the filename doesn't have to match.
- The body becomes the subagent's system prompt. The subagent gets that prompt plus environment details, not the Claude Code system prompt.
- A subagent starts with a fresh context: its system prompt, the delegation message Claude writes, CLAUDE.md files (unless `omitClaudeMd`), a git status snapshot, and any skills in `skills`. It does not see the main conversation's history.

## Frontmatter Fields

Only `name` and `description` are required. Field names are camelCase and must match exactly: Claude Code ignores an unrecognized field without an error.

| Field | Required | Values and behavior |
|-------|----------|---------------------|
| `name` | Yes | Unique identifier, at most 256 characters, such as `code-reviewer`. Can't contain `:` (reserved for plugin-scoped names) or start with `-` |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | Allowlist, as a comma-separated string (`Read, Grep, Bash`) or a YAML list. Omit to inherit every tool available to subagents. If no entry resolves to a tool, the subagent usually fails to launch. Use `skills`, not `Skill` here, to preload skills |
| `disallowedTools` | No | Denylist, same format as `tools`, removed from the inherited or specified list. An entry with a specifier such as `Bash(git push *)` still removes the whole tool |
| `model` | No | `sonnet`, `opus`, `haiku`, `fable`, a full model ID such as `claude-opus-5-5`, or `inherit`. See [Choosing model](#model) |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, or `manual` (alias for `default`). Ignored for plugin subagents |
| `maxTurns` | No | Maximum agentic turns. At the limit, output is returned marked partial and Claude can resume the subagent |
| `autoCompactWindow` | No | Lower this subagent's auto-compact window to a token count from `100000` to `1000000`. Requires v2.1.296+ |
| `skills` | No | Skills whose full content is preloaded at startup (first 32 names). The subagent can still invoke unlisted skills through the Skill tool |
| `mcpServers` | No | List of server names already configured (`- github`) or inline definitions keyed by server name, using the `.mcp.json` schema (`stdio`, `http`, `sse`, `ws`). Ignored for plugin subagents |
| `hooks` | No | Lifecycle hooks scoped to this subagent. Ignored for plugin subagents |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | `true` keeps the subagent in the background even when Claude asks to wait for it |
| `omitClaudeMd` | No | `true` starts the subagent without user, project, and local CLAUDE.md files (managed policy files still load). Ignored with `--agent`. Requires v2.1.271+ |
| `effort` | No | `low`, `medium`, `high`, `xhigh`, `max`; available levels depend on the model |
| `isolation` | No | `worktree` runs the subagent in a temporary git worktree, auto-cleaned if it makes no changes |
| `color` | No | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, or `cyan` |
| `initialPrompt` | No | Auto-submitted first user turn when the agent runs as the main session (`--agent` or the `agent` setting). Ignored for plugin subagents |
| `experimental` | No | Map. Its `cacheTtl` key takes `5m` or `1h` for this subagent's prompt cache lifetime. Requires v2.1.248+ |

```yaml
---
name: repo-auditor
description: Audits a large repository and reports what it finds
experimental:
  cacheTtl: 1h
---
```

### Files Claude Code skips

A file in a project, user, or managed `agents` directory is skipped (without a message in the session) when:

- It has no `name` (treated as documentation)
- The opening `---` is not the first line
- `name` starts with `-`, contains `:`, or is longer than 256 characters
- It has `name` but no `description`
- The YAML doesn't parse

Run `claude --debug` to see the reasons in the debug log; it also names unrecognized top-level fields (search for `does not recognize or apply`, v2.1.296+). `claude plugin validate .claude/agents` finds frontmatter that doesn't parse, but not a missing `name` or a misspelled field. A plugin subagent with no `name` or unparsable frontmatter still loads, named after its file.

## Choosing the Important Fields

### model

Claude Code resolves a subagent's model in this order:

1. The per-invocation `model` parameter Claude passes
2. The `model` frontmatter (`inherit` selects the main conversation's model)
3. The `CLAUDE_CODE_SUBAGENT_MODEL` environment variable
4. The main conversation's model

| Choice | Use when |
|--------|----------|
| Omit | Default. Lets the user's env var or Claude's per-call choice decide |
| `inherit` | The agent should always match the main conversation, such as a reviewer whose judgment should equal the session's |
| `haiku` | Cheap, high-volume, well-defined work (the docs suggest it for a lower-cost `Explore` override) |
| `sonnet`, `opus`, `fable`, or a full ID | The job needs a specific model regardless of the session |

Caveats:

- A family alias that matches the main conversation's family (e.g. `opus` while the session runs Opus) resolves to the main conversation's exact model, including any `[1m]` suffix.
- An organization `availableModels` allowlist can substitute another model; Claude Code warns when it does.
- With `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`, the `model` field is ignored.
- Subagents inherit the main conversation's extended thinking setting; there is no per-subagent thinking field.

### effort

`effort` overrides the session's effort level while this subagent runs. A per-invocation `effort` parameter overrides the field, and the `CLAUDE_CODE_EFFORT_LEVEL` environment variable overrides both.

- Lower effort fits mechanical, high-volume jobs such as log triage or file search.
- Higher effort fits jobs that trace logic or weigh edge cases, such as review, debugging, or security analysis.
- Omit it to follow the session.

### permissionMode

Unset, the subagent inherits the main conversation's permission mode. When set, the main conversation's mode decides whether it applies:

| Main conversation mode | Subagent runs in |
|------------------------|------------------|
| `bypassPermissions`, `acceptEdits`, or auto | The main conversation's mode; the field is ignored |
| `plan` | Plan mode (if the field is `dontAsk`, prompts are also denied) |
| `default` or `dontAsk` | The field's mode, except `bypassPermissions` (keeps the main mode) and `auto` when auto mode isn't available |

| Mode | Behavior | Use when |
|------|----------|----------|
| `default` | Prompts for permission | You want approval on each sensitive call |
| `acceptEdits` | Auto-accepts file edits and common filesystem commands in the working directory | A writer agent whose edits you review afterwards |
| `auto` | A background classifier reviews commands and protected-directory writes | Long writer runs without prompts, where auto mode is available |
| `dontAsk` | Auto-denies anything that would prompt; explicitly allowed tools still work | Unattended agents that should fail closed |
| `bypassPermissions` | Skips prompts, only when the main conversation already does | Rarely; it can't escalate on its own |
| `plan` | Read-only exploration | Research agents that must not change anything |

Background subagents surface their permission prompts in the main session. Plugin subagents ignore `permissionMode`.

### isolation

`isolation: worktree` gives the subagent an isolated copy of the repository in a temporary git worktree.

- The worktree branches by default from the repository's default branch, not the parent session's `HEAD`. The agent won't see uncommitted or unmerged work on the user's current branch.
- Bash commands are confined to the worktree; a command that targets the main checkout fails.
- The worktree is removed automatically if the subagent makes no changes.
- With agent teams enabled, a subagent Claude spawns with a `name` launches as a teammate instead, and a frontmatter `isolation` doesn't prevent that.

Use it for writers that may run in parallel with other writers or with the user. Don't use it for reviewers of the user's current changes.

## Tools

Subagents inherit the main conversation's built-in and MCP tools, narrowed by two filters:

1. Every subagent loses `AskUserQuestion`, `EnterPlanMode`, `EndConversation`, `ScheduleWakeup`, `WaitForMcpServers`, `Workflow`, `ExitPlanMode` (unless `permissionMode: plan`), and `Agent` at the nesting depth limit, even if listed in `tools`.
2. Background subagents (the default for subagents Claude spawns) keep every MCP tool but only these built-ins: `Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, `Artifact`, and `SubagentHandback` for a subagent that reports through it.

When both `tools` and `disallowedTools` are set, `disallowedTools` is applied first, then `tools` is resolved against what remains. A tool listed in both is removed.

```yaml
# Allowlist: only these tools, no MCP tools
tools: Read, Grep, Glob, Bash

# Denylist: everything inherited except file writes (keeps Bash and MCP tools)
disallowedTools: Write, Edit

# Reviewer: both, so Write and Edit stay out even if tools is widened later
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
```

| Goal | Field | Entry |
|------|-------|-------|
| Every tool from one MCP server | `tools` | `mcp__github__*` |
| Withhold one server's tools | `disallowedTools` | `mcp__github` or `mcp__github__*` |
| Withhold all MCP tools | `disallowedTools` | `mcp__*` |
| Block nested subagents | `tools` / `disallowedTools` | omit `Agent` / list `Agent` |
| Block skill invocation | `tools` / `disallowedTools` | omit `Skill` / list `Skill` |

To keep Bash but block specific commands, a `disallowedTools` entry won't work (it removes all of Bash). Use a `PreToolUse` hook, or a `permissions.deny` rule such as `Bash(git push *)` in settings (that rule applies to the whole session).

## Hooks

Frontmatter hooks run only while the subagent is active. All hook events are supported; `Stop` becomes `SubagentStop` at runtime.

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

The hook command receives the tool input as JSON on stdin and blocks the call by exiting with code 2. Make the script executable. Hooks in a project agent run only after the user accepts the workspace trust dialog for that folder.

## Memory

| Scope | Location | Use when |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/<name-of-agent>/` | Learnings apply across all projects |
| `project` | `.claude/agent-memory/<name-of-agent>/` | Project-specific and shareable via version control (the docs' recommended default) |
| `local` | `.claude/agent-memory-local/<name-of-agent>/` | Project-specific but not checked in |

With memory enabled, Read, Write, and Edit are enabled automatically so the agent can manage its memory files. The docs don't say whether `disallowedTools` overrides this, so don't combine `memory` with a read-only reviewer without testing it. Memory has no effect when auto memory is turned off.

## Storage Locations and Precedence

When several subagents share a `name`, the higher-priority location wins:

| Priority | Location | Scope | How to create |
|----------|----------|-------|---------------|
| 1 (highest) | Managed settings (`.claude/agents/` in the managed settings directory) | Organization | Deployed by administrators |
| 2 | `--agents` CLI flag (JSON) | Current session | Pass JSON when launching Claude Code |
| 3 | `.claude/agents/` | Current project | Write the file |
| 4 | `~/.claude/agents/` | All your projects | Write the file |
| 5 (lowest) | A plugin's `agents/` directory | Where the plugin is enabled | Install the plugin |

Details:

- Project agents are found by walking up from the working directory to the repository root. If nested `.claude/agents/` directories define the same name, the one closest to the working directory wins.
- Two files with the same `name` under one `.claude/agents/` tree: only one loads, by filesystem read order. `/doctor` reports these.
- Directories added with `--add-dir` or `/add-dir` also load their `.claude/agents/`.
- Plugin agents get scoped names: `agents/review/security.md` in `my-plugin` registers as `my-plugin:review:security`. Plugin agents ignore `permissionMode`, `hooks`, `mcpServers`, and `initialPrompt`; copy the file into `.claude/agents/` if it needs them.
- `--agents` JSON keys are agent names; each value takes `prompt` (the body) plus `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `autoCompactWindow`, `skills`, `initialPrompt`, `memory`, `effort`, `background`, `omitClaudeMd`, and `isolation`. `color` and `experimental` are ignored there.
- A user or project agent named `Explore` replaces the built-in Explore agent.

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### Reloading

Claude Code watches `~/.claude/agents/` and `.claude/agents/` and picks up added or edited files within seconds. Restart when:

- The `agents` directory didn't exist when the session started
- The agent lives under an `--add-dir` directory
- The session was started with `--disable-slash-commands`

## Description Best Practices

The description is the trigger. Include what the agent does, when to invoke it, and its scope. Add "use proactively" to encourage automatic delegation. Keep it short: Claude Code warns at startup when all subagent descriptions together pass 15,000 tokens.

```yaml
# Good - specific and actionable
description: Reviews TypeScript changes in src/api/. Use after modifying API endpoints, middleware, or request handlers.

# Bad - vague
description: Helps with code review.
```

## System Prompt Body

```markdown
---
name: api-reviewer
description: Reviews API changes in src/api/. Use for PRs modifying routes or controllers.
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
---

# API Reviewer

You review API code changes for this repository. Do not modify files.

## Repository Context
- API source: `src/api/`
- Route definitions: `src/api/routes/`
- Shared types: `src/types/`
- Tests: `npm test`

## Review Guidelines
1. Run `git diff` to see the changes
2. Check error handling patterns
3. Verify route naming conventions
4. Ensure request validation exists
5. Run the tests for changed routes

## Output Format
- Summary of changes reviewed
- Issues found (with file:line references)
- Open questions that need the user's decision
```

## Invoking

- **Automatic**: Claude delegates when a task matches the description.
- **Natural language**: "Use the api-reviewer subagent to check my changes."
- **@-mention**: `@"api-reviewer (agent)"` or `@agent-api-reviewer` (plugin agents: `@agent-my-plugin:api-reviewer`) guarantees that agent runs.
- **Whole session**: `claude --agent api-reviewer`, or `"agent": "api-reviewer"` in `.claude/settings.json`.

To block an agent, add `Agent(agent-name)` to `permissions.deny` in settings.
