# Fresh-session GPT-6.1 Terra / Claude Sonnet 5.5 — low

The earlier Codex runs already used new ephemeral sessions with no parent chat
handoff, user config/rules, project documents or skills. This run additionally
places artifact workspaces outside repository ancestors and audits native session
IDs, Claude tool inventories and auth provenance. It does **not** claim zero total
context: common task/instructions, native core/tool/managed policies remain.

| Measured dimension | GPT-6.1 Terra low | Claude Sonnet 5.5 low |
|---|---:|---:|
| Same GPQA Diamond 8-question subset, two trials | 7/8, 8/8 | 6/8, 6/8 |
| Same ledger hidden behavioral checks, one attempt | 13/13 | 13/13 |
| Same research reproduction checks, one attempt | 7/7 | 7/7 |
| Structure, new anonymous joint LLM review | 6/6 | 6/6 |
| Research interpretation, new anonymous joint LLM review | 6/6 | 4/6 |

There are eight unique questions, not sixteen independent questions per model.
Structure/research opinions are not objective accuracy or statistical evidence of
a general model ranking. Single coding/research attempts have no variance estimate.
The prior Sol 6.1/6.2 measurements used the same frozen tasks; they are historical
references rather than simultaneous controls or identical cross-provider harnesses.

## What was isolated and verified

- Codex 0.170.0 requested `gpt-6.1-terra`, effort low, native ChatGPT login.
  Commands used `--ephemeral --ignore-user-config --ignore-rules`, project-doc bytes
  zero, common replacement instructions, skills/plugins/apps/hooks off and explicit
  memories off. No resume/fork/continue or parent conversation was supplied.
- Claude Code 2.1.327 requested `claude-sonnet-5-5`, effort low, native Claude.ai
  first-party subscription login. It used safe-mode, restricted mode, no setting
  sources, no persistence, a fresh UUID, strict empty MCP configuration, disabled
  slash commands/skills and common replacement system text. `--bare` was avoided
  because this installed version documents API-only auth for that mode.
- Claude raw init/assistant/result fields reported exactly the requested model.
  Launch UUID, init session and final session matched in every Claude call.
  Tools were empty for questions, and exactly Bash/Edit/Read/Write for artifacts.
  Skills, personal plugins and MCP lists were empty, permission mode was dontAsk,
  API-key source was none, and server-tool/web-search counts were zero.
- All **eight native session IDs were distinct**. Question directories started
  empty. Artifact directories were fresh copies outside Git repository ancestors;
  no ancestor AGENTS.md/CLAUDE.md existed. Starting tasks, prompts, input data and
  grader hashes matched the previous expanded Sol experiment exactly.
- Claude still reported five reviewed built-in components: security defaults,
  agents-md, telemetry, privacy and plugin authoring. These are retained native
  host components, not evidence that personal plugins/skills were supplied. Their
  exact inventory is preserved in [context-audit.json](context-audit.json).
- Native backend snapshots/full system prompts are not independently attested.
  Codex's tool/catalog exclusion is verified from launch controls; its stream does
  not expose an equivalent complete initial inventory. Cross-provider low labels,
  token counts and native tool schemas do not mean equal compute or identical context.

No credentials, email, organization IDs or private conversation IDs are published.
Original native streams and actual session IDs remain in local ignored output.
The public audit preserves verification booleans, settings, safe inventories and hashes.

## Research outcome versus interpretation

Both generic analysis programs passed original, reordered, gapped, scaled and
constant input checks, saved-results reproduction and report presence. Both kept
the input CSV and metadata unchanged. Their numerical results match the trusted
reference, including LMC first-difference correlation **+0.0787606**.

The anonymous review rated Sonnet's research interpretation 4/6. Its report table
contains the small positive correlation, while the conclusion says no positive
association was found; it also says level slopes mostly reflect time trends
without identifying their contribution. The reviewer considered those statements
stronger than the analysis establishes. Terra received 6/6. These are the fixed
reviewer's opinions with actual report references, not altered numerical scores.

The same `gpt-6.2-astra` judge reviewed all four historical/new anonymous artifact
sets in a fresh joint review, with identities withheld and no code execution.
Its provider affiliation may still bias judgments. This is separate from the
earlier two-candidate review; previous scores were not overwritten. In this joint
review, the 5,001-digit diagnostic was explicitly unweighted and all structures
received 6/6. Three implementations (Sol 6.1, Terra 6.1, Sonnet) fail that extreme
case; Sol 6.2 handles it. No 13-check acceptance score was changed.
See [joint-judge-scores.json](joint-judge-scores.json) and the subsequently revealed
[mapping](joint-judge-mapping.json).

## Execution and control audit

Eight contestant CLI launches completed: four questions, two implementations and
two research analyses. No model was selectively regenerated or repaired. There was
one separate anonymous joint artifact reviewer, plus normal harness verification.
Native subscription authentication was used; no separately billed SDK/API adapter
was selected. Claude's raw API-price estimates are not reported as subscription bills.

| Track | Terra wall time | Sonnet wall time |
|---|---:|---:|
| GPQA mean of two | 12.065 s | 14.435 s |
| Implementation | 51.560 s | 36.190 s |
| Research | 54.240 s | 49.687 s |

Times include startup/network/tool execution; caches and harnesses differ. They
are descriptive rather than an intrinsic-speed benchmark. Terra's visual/browser
capabilities were not tested; all tasks were text/code/data.

The initial Claude normalizer mistook its built-in catalog for personal plugins.
Offline correction validated raw and original normalized hashes, replayed the old
classification and recomputed the reviewed one. Two question statuses changed
without any new contestant call. Raw records remain preserved, with corrections
in [evidence.json](evidence.json). Actual native IDs/menus/auth/server-tool fields
were also audited after the normalizer guards were strengthened.

Implementation requested native Claude sandbox/network restrictions but did not
yet set failIfUnavailable. Effective native isolation for that phase is not attested.
The research launcher added exact model matching and fail-closed sandbox startup
before either research contestant launched. Requested settings alone are not proof
of every managed-policy outcome. All grading executed separately in the unchanged
pinned, read-only, unprivileged, network-disabled Python Docker environment, with
collected artifact hashes checked before/after. No network/grader/sibling/model
access was observed in the recorded task commands.

Native evidence checks now reject mismatched session IDs, unexpected tool inventories,
permission modes/auth sources, server-side tools, and host-map tampering. Sandbox
startup requests fail closed in future artifact profiles. Deterministic tests cover
these failures using fake native executables; no model calls are made by CI.

## Reproduction and provenance

The same public task/starter/grader files and source notices remain in
[the previous expanded-low directory](../expanded-low/EVALUATION.md). New actual
submissions are under [artifacts](artifacts). [evidence.json](evidence.json) contains
frozen plans, safe execution receipts and artifact hashes; [launcher-snapshots.json](launcher-snapshots.json)
preserves exact source at each phase's launch. Raw local data are in
`output/2026-11-18-terra-sonnet-low/`, including the archived actual artifact runs.

Primary behavior references:
[Claude CLI](https://code.claude.com/docs/en/cli-reference),
[model/effort controls](https://code.claude.com/docs/en/model-config),
[native sandbox limits](https://code.claude.com/docs/en/sandboxing),
[Codex configuration](https://developers.openai.com/codex/config-reference).
Imported research data retain their ODC-By notices; own harness/evaluation code
remains MIT. This is not a full official GPQA, SWE-bench or DiscoveryBench score.
