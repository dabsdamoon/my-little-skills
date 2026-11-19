# Fresh Codex and Claude subscription sessions

Both runners support explicit host selection. Models listed in `--claude-models`
run through the native Claude Code CLI; all other selected IDs run through Codex.
This is a comparison of model plus native harness, not identical provider APIs.

```bash
python3 <skill-dir>/scripts/codex_benchmark.py plan \
  --out output/terra-sonnet-low --suite /path/to/frozen-suite.json \
  --models gpt-6.1-terra claude-sonnet-5-5 \
  --claude-models claude-sonnet-5-5 --effort low --trials 2
python3 <skill-dir>/scripts/codex_benchmark.py run \
  --out output/terra-sonnet-low --max-calls 4
python3 <skill-dir>/scripts/codex_benchmark.py report \
  --out output/terra-sonnet-low
```

The artifact collector accepts the same `--claude-models` and `--claude` executable
options. Freeze one common starter/task/grading specification for both hosts.
Check current models and effort support; these version IDs are an example, not
an automatic upgrade policy. A label such as `low` does not guarantee equal compute
across models or providers. Do not interpret provider tokenizer counts as equal work.

## Authentication and settings

Preflight verifies every required host before any contestant launch. Codex must
report ChatGPT login. Claude must report `loggedIn`, `authMethod=claude.ai`, and
`apiProvider=firstParty` through `claude auth status --json`. Only safe receipt fields
are preserved; no tokens, email, organization IDs or keychain data are extracted.
The child environment preserves ordinary auth-store locations, including an existing
CODEX_HOME or CLAUDE_CONFIG_DIR, without relocating credentials or inheriting API
keys/provider/endpoint overrides. No provider SDK or API fallback is selected.

Claude uses `--safe-mode --restricted --no-session-persistence`, a fresh UUID,
empty setting sources and strict empty MCP configuration, disabled slash commands,
and common replacement system text. Question trials have no tools. Artifacts have
only Bash/Read/Write/Edit, restricted writes and requested sandboxed Bash with network off,
`failIfUnavailable=true` and no unsandboxed retry. Model matching uses
`availableModelsMatch=exact` with `enforceAvailableModels=true` and an empty configured
fallback chain constrain model substitution; reported model mismatches invalidate
an attempt even if it returned a plausible answer. A requested setting alone does
not attest native enforcement; disclose any verification limit.

Claude 2.1.327 still reports built-in security/privacy/agents-md/telemetry/authoring
components in safe mode. The parser records them and accepts only reviewed exact
built-in name/path/source triples; personal or unknown plugins invalidate a trial.
To rule out ancestor-document discovery for artifacts, place the experiment under
a fresh system temporary directory outside repositories, verify no ancestor
AGENTS.md/CLAUDE.md, and archive results after checking collected hashes.

Do **not** use `--bare` for subscription benchmarking. The installed Claude Code
2.1.327 help and [official CLI reference](https://code.claude.com/docs/en/cli-reference)
describe that mode as skipping OAuth/keychain and requiring API auth. Safe mode
disables personal customizations while keeping native subscription authentication.

## What “fresh” means

No parent conversation, resume/continue/fork history, personal skills, project rules
or automatic memory is deliberately supplied. Codex ignores user config/rules,
sets project-doc bytes to zero, disables memories/catalog/plugins/apps/hooks, and
uses a new ephemeral session. Each question cwd starts empty; each artifact cwd
starts with the same frozen files. Common instruction and task hashes are recorded.

This is **not zero total context**. Native tool schemas, system/managed policies,
date/cwd metadata and provider infrastructure can remain. Their absence cannot be
inferred from a new session ID or input-token count. Record these controls and
limits rather than asserting perfect raw-model isolation. Prompt caching is not
conversation-history reuse.

## Evidence and failures

Claude's original stream is `run-*.native.jsonl`; a separate normalized stream feeds
the common grader. Final text is copied without repair. Reported model IDs, native
tool/context inventories, permission denials, usage and session IDs are recorded.
The text audit cross-checks native hashes and recomputes normalization before scoring.
It checks native tools, permission mode, API-key source, server-tool counters and
init/result session IDs against the launch UUID. Run hosts must match the frozen
provider map, so removing a host field cannot skip native-evidence validation.
Missing/changed evidence, unexpected models/ambient skills/MCP, permission failures
and malformed host streams do not silently become quality zeros or successful runs.

Native Claude input usage includes uncached input plus cache-read/cache-write input
in the normalized total; each component remains available. Its API-price cost
estimate, if present in raw output, is not a subscription bill and is not reported
as money spent. Requested effort is recorded; do not claim independently measured
backend reasoning budgets when the host does not expose them.

Primary controls: [Claude CLI](https://code.claude.com/docs/en/cli-reference),
[model and effort settings](https://code.claude.com/docs/en/model-config),
[sandbox](https://code.claude.com/docs/en/sandboxing),
[Codex config](https://developers.openai.com/codex/config-reference).
