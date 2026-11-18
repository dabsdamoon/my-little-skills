---
name: model-quality-compare
description: Use when comparing LLM models or versions, benchmarking GPT or Claude quality, choosing a model for a task, or checking a claimed model upgrade under a small subscription budget.
license: MIT
---

# Model Quality Compare

Compare identical frozen tasks under explicit controls. Report capability,
reliability and efficiency separately. A tiny pilot is not a general ranking.

## Choose a route

| Request | Route |
|---|---|
| GPT versions available in Codex with ChatGPT login | Subscription pilot below |
| Claude subscription tiers on one product task | [Claude workflow](references/claude-workflow.md) |
| Named public benchmark or another provider | Official dataset/protocol and an explicitly authorized adapter |

A skill cannot switch its host model. Use an actual model-pinned runner. Verify
available IDs; never substitute a model or silently change subscription to API billing.

## Design

1. Read [metrics.md](references/metrics.md). Choose dimensions relevant to the user's
   decision. Keep manufacturer scores separate from measurements you will run.
2. Match model family, reasoning effort, tools, prompt and context. Record requested
   IDs. Versioned names may be moving aliases, not verified backend snapshots.
3. Freeze tasks, objective answers and graders before observing outputs. Independently
   validate new keys. Preserve failures and ceilings; follow-ups are new experiments.
4. Default budget: two models × two trials = **four calls**, no paid judge. This
   consumes subscription quota and bounds calls, not exact tokens or duration.

## Codex subscription pilot

Requires Python 3.10+, compatible `codex exec --help`, and `codex login status`
reporting ChatGPT login. The bundled suite has 24 original text cases, four each
for reasoning, knowledge, code comprehension, instructions, grounding and Korean.
It is not MMLU, GPQA, IFEval or HumanEval; code generation and agents are unmeasured.

Use this skill's actual directory for `<skill-dir>`. Choose a new experiment path:

```bash
python3 <skill-dir>/scripts/codex_benchmark.py plan \
  --out output/gpt-sol-pilot \
  --models gpt-6.1-sol gpt-6.2-sol --trials 2 --effort medium
python3 <skill-dir>/scripts/codex_benchmark.py run \
  --out output/gpt-sol-pilot --max-calls 4
python3 <skill-dir>/scripts/codex_benchmark.py report \
  --out output/gpt-sol-pilot
```

The runner enforces ChatGPT login, allowlists OS environment variables (preserving
normal credential-store locations), removes API/provider overrides, ignores user
config/rules, replaces built-in instructions with common instructions, disables
tools/plugins/skills, and uses an empty temporary cwd per trial. Native harness
or managed context may remain: this measures a **Codex session**, not a bare model.
Do not bypass unsupported controls or change settings for just one contestant.

Runs are sequential, alternating forward/reverse order (ABBA for two models).
The budget counts contestant CLI launches; Codex may internally retry transport.
Resume skips every recorded attempt, including failures; no automatic retries.
Inspect interrupted attempts/stale `.run-lock` before clearing a lock. Intentional
retries use a new experiment. Never retry only a weak result until it improves.

## Deliver

`plan.json` freezes settings, suite and hashes. `runs.json`, answers, events and
stderr preserve execution evidence. `results.json` records per-case expected/actual
answers, categories, trial spread, agreement, coverage, errors and token usage.
`report.html` and `report.md` summarize the comparison. Show category results,
failed examples, settings and limits, and link the visual report.

Completed invalid-format responses receive zero; missing cases fail individually.
Infrastructure errors and tool-control violations are **N/A**, with coverage shown.
Missing or changed evidence is an evidence error with N/A quality. Orphaned
artifacts or duplicate/foreign run records block launches rather than spend again.
CLI startup warnings are diagnostics, not tool use. Offline parser corrections
must preserve raw records, disclose corrections and make no new contestant calls.

Two repetitions do not double the unique case count. A ceiling/tie is inconclusive.
CLI wall time is not TTFT. Subscription quota is not an API dollar estimate.
Subjective tasks require a blinded rubric and separately labeled judge opinion;
objective ground truth takes priority.
