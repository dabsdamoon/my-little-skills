# Codex Custom Agents

When the user works in Codex, emit a Codex custom agent alongside (or instead of) the Claude Code subagent. Everything here comes from the Codex subagents docs listed under Sources in SKILL.md.

## Signs the User Works in Codex

- They say so, or this skill is running inside Codex
- The repository has `AGENTS.md` or a `.codex/` directory
- `~/.codex/` exists on the machine

If they use only Codex, write only the TOML file. If they use both, write both and keep the instructions equivalent.

## Location and Identity

| Location | Scope |
|----------|-------|
| `~/.codex/agents/` | Personal agents |
| `.codex/agents/` | Project-scoped agents |

- One standalone TOML file per agent.
- Codex identifies the agent by its `name` field. Matching the filename to the name is a convention, not a rule.
- A custom agent whose name matches a built-in (`default`, `worker`, `explorer`) takes precedence over the built-in.
- The docs don't state which wins when a personal and a project agent share a name. Avoid duplicates rather than relying on either.
- The docs' examples use snake_case names in hyphenated files (`name = "pr_explorer"` in `pr-explorer.toml`). Follow that; the docs don't say whether hyphens are accepted in `name`.

## File Schema

Required:

| Key | Type | Purpose |
|-----|------|---------|
| `name` | string | Name Codex uses when spawning or referring to the agent |
| `description` | string | Human-facing guidance for when Codex should use the agent |
| `developer_instructions` | string | Core instructions that define the agent's behavior |

Optional model keys: `model`, `model_reasoning_effort`, `model_reasoning_summary`, `model_verbosity`. Accepted values are in the Codex configuration reference, which this skill hasn't verified; use values the user's Codex install accepts.

Optional capability reductions (set to `false`): `features.shell_tool`, `features.apps`, `features.plugins`, `features.memories`, `features.request_permissions_tool`.

Optional skill controls: `[[skills.config]]` entries with `path` and `enabled = false` to disable one skill, `skills.bundled.enabled = false` for bundled skills, `skills.include_instructions = false` to omit the automatic skills instructions block.

### What a custom agent can't set

A custom agent inherits the parent session's permissions, provider, and MCP servers. These keys don't override the parent when placed in an agent file:

- `sandbox_mode`
- `approval_policy`
- `model_provider`
- `mcp_servers`

The service tier also follows the root session. Instructions can tell an agent not to edit files, but that doesn't create a read-only sandbox. Set sandbox and approval controls on the parent session, and configure MCP servers there.

## Model and Reasoning Resolution

- If the file sets `model` or `model_reasoning_effort`, the file wins.
- Otherwise Codex resolves each from an explicit spawn value, then the `[agents]` default in `config.toml`, then the parent's value.
- If a spawn value or `[agents]` default picks a model without an effort, Codex uses that model's default effort. A file that sets only `model` keeps that resolved effort, so also set `model_reasoning_effort` if the model doesn't support it.
- Omit both keys to inherit the parent's model and effort.

The docs' guidance, as checked: `gpt-6.1-sol` for demanding, multi-step agents; `gpt-6-luna` for fast, narrowly scoped, high-volume agents. Reasoning effort levels include `low`, `medium`, `high`, `xhigh`, `max`, and `ultra`, depending on the model; `high` suits reviewer and security-focused agents. Model names change often, so prefer omitting `model` unless the user asks for one.

## Global `[agents]` Settings (config.toml)

| Key | Purpose |
|-----|---------|
| `agents.enabled` | Enable or disable multi-agent tools (default `true`) |
| `agents.max_concurrent_threads_per_session` | Cap concurrently open spawned-agent threads (legacy alias `agents.max_threads`) |
| `agents.default_subagent_model` | Default model for spawned agents |
| `agents.default_subagent_reasoning_effort` | Default reasoning effort for spawned agents |
| `agents.interrupt_message` | Record a model-visible message when an agent turn is interrupted (default `true`) |

## Invocation Differs from Claude Code

Per the docs, local Codex releases spawn agents after a direct request ("spawn one agent per point") or an applicable `AGENTS.md` or skill instruction. A good `description` alone isn't documented to trigger delegation the way it does in Claude Code. Tell the user how to call the agent by name, and offer to add a line to `AGENTS.md` if they want it used routinely. In the CLI, `/subagents` switches between running agent threads.

## Mapping from Claude Code Fields

| Claude Code frontmatter | Codex custom agent |
|-------------------------|--------------------|
| `name` | `name` (snake_case per the docs' examples) |
| `description` | `description` |
| Markdown body | `developer_instructions` |
| `model` | `model`, with a Codex model name (Claude aliases don't apply) |
| `effort` | `model_reasoning_effort` |
| `tools` / `disallowedTools` | No per-tool list. `features.shell_tool = false` removes the shell; other limits go in the instructions |
| `permissionMode` | None; inherits the parent's sandbox and approval settings |
| `mcpServers` | None; configure servers in the parent session |
| `skills` | Skills are inherited; disable individual ones with `skills.config` |
| `memory` | `features.memories = false` disables memories; no per-agent memory directory is documented |
| `isolation`, `maxTurns`, `background`, `hooks`, `color`, `initialPrompt`, `omitClaudeMd` | No equivalent documented on the subagents page |

## Example: Reviewer

Claude Code reviewers get Bash so they can run `git diff` and tests. In Codex, keep the shell (it's needed for the same reason) and state the no-edit rule in the instructions.

`.codex/agents/api-reviewer.toml`:

```toml
name = "api_reviewer"
description = "Reviews API changes in src/routes/, src/middleware/, and src/controllers/. Use after Express endpoints, middleware, or request handlers change."
model_reasoning_effort = "high"
developer_instructions = """
You review API code changes for node-backend.
Do not edit files. Use the shell only for git and test commands.

Process:
1. Run git diff main...HEAD -- src/routes src/middleware src/controllers.
2. Read each changed file and its tests in tests/ (Jest, *.test.ts).
3. Run npx jest for the affected tests.

Check error handling, request validation, test coverage, and hardcoded secrets.
If a finding depends on intent you can't infer, list it under Open Questions instead of guessing.

Report: summary, issues as [HIGH/MED/LOW] file:line - description, open questions, verdict.
"""
```

A research agent that never needs a shell:

```toml
name = "docs_researcher"
description = "Looks up framework and API documentation and returns cited answers."
developer_instructions = """
Confirm APIs, options, and version-specific behavior from documentation.
Return concise answers with exact references. Do not make code changes.
"""

[features]
shell_tool = false
```

## TOML Notes

- `"""` strings treat backslashes as escapes. Use `'''` for instructions that contain backslashes or regexes.
- Put top-level keys before any `[table]` or `[[array]]` header; keys after a header belong to that table.
- Check the file parses: `python3 -c 'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' .codex/agents/api-reviewer.toml`
