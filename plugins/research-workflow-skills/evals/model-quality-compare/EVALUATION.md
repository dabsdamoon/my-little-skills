# GPT Sol subscription pilot — 2026-11-18

**Result: ceiling, no general winner.** Both requested models answered all 24
original cases correctly on both trials. This validates the execution and grading
path, but this small suite did not discriminate frontier-model quality.

| Requested model | Trial 1 | Trial 2 | Mean CLI time | Mean reported output tokens |
|---|---:|---:|---:|---:|
| `gpt-6.1-sol` | 24/24 | 24/24 | 15.392 s | 565 |
| `gpt-6.2-sol` | 24/24 | 24/24 | 16.7065 s | 472 |

Each of the six categories scored 4/4 in each trial: reasoning, knowledge, Python
code comprehension, instruction following, supplied-source grounding and Korean.
Answer agreement was 100%. Repetitions are not 48 independent questions/model.
The observed times and token counts are descriptive, not an established efficiency
advantage. Input tokens differed by model/harness; requested effort is not equal compute.

## Conditions and budget

- Created 2026-11-18 09:34 UTC; Codex CLI `0.170.0`, existing ChatGPT login.
- Four contestant CLI launches, sequential order 6.1 → 6.2 → 6.2 → 6.1, medium effort.
- Identical question and replacement-instruction bytes; tools/plugins/skills disabled,
  user config/rules ignored, empty temporary cwd per trial. No provider SDK or paid judge.
- Separate API billing was not selected. Subscription quota was consumed. CLI-internal
  transport retries, if any, are not additional independent trials.
- Requested aliases, not independently resolved immutable backend snapshots. Native
  harness context and temporary cwd can differ; this is a Codex-session comparison.
- No code generation/execution, visual, long-context, safety or agent benchmark was run.

## Audit and limitations

The initial collector misclassified Codex's `item.type=error` startup notice about
two under-development flags as a tool call. Every raw event stream actually had
that warning, one answer, and a completed turn. An offline parser correction
reclassified all four, preserved original records, and made no model calls.
The answers match their collection-time hashes and the final raw agent messages.

This first pilot predates runner/event hash capture and the complete child-env
allowlist. The initial environment filter removed OpenAI/Anthropic API variables
but did not attest additional `CODEX_*` endpoint/auth overrides. Those limitations
are disclosed, not retroactively “verified.” Current runs freeze the runner hash,
capture event hashes, allowlist OS variables, validate manifests/orphaned artifacts,
and report corrupt evidence as N/A. Native ChatGPT login still works with that
allowlist, checked locally without another model invocation.

[evidence.json](evidence.json) preserves publishable settings, answers, usage and
corrections without local usernames, thread IDs or credential paths. Its event
hashes are labeled **archival**, not collection-time. The prompt and instruction
bytes are preserved in [frozen-prompt.txt](frozen-prompt.txt) and
[frozen-instructions.txt](frozen-instructions.txt). Raw local logs and interactive
HTML are in the worktree's ignored `output/2026-11-18-gpt-sol-pilot/` directory.

## Skill and harness verification

Baseline usability review found the previous Claude-only guide could not execute
this task. Forward review found the revised guide supplied runnable commands,
subscription controls and appropriate interpretation, with no blocking guide gap.
An independent reviewer recomputed the answer key and checked raw responses.

Eleven deterministic CLI tests cover grading/types, duplicate JSON, frozen-file
changes, budget/resume, auth and endpoint overrides, startup diagnostics, missing
and corrupt artifacts, legacy event cross-checks, manifest/orphan protection and
generic report labels. Only the external Codex executable is faked. The live pilot
is distinct from these automated tests and skill-authoring reviews.

## General metrics and external evidence

See the skill's [metric guide](../../skills/model-quality-compare/references/metrics.md)
for MMLU-Pro, GPQA, IFEval, EvalPlus, SimpleQA, reliability and efficiency measures.
Our 24 questions reproduce none of those public protocols.

Separately, OpenAI reports a **5.3-point improvement on GDPval v2** for 6.2 Sol over
6.1 Sol. This is manufacturer-reported professional-work evidence, not our pilot
score and not the Agents' Last Exam result for Astra.
[Official release](https://openai.com/index/introducing-gpt-6-2-astra-sol/).

A harder follow-up needs a new frozen suite/experiment and a separately counted
call budget. Retain this ceiling result; do not change answers or selectively
rerun models to create a winner.
