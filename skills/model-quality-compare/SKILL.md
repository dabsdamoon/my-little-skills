---
name: model-quality-compare
description: Run a controlled, blinded quality shootout between Claude subscription model tiers (Opus, Sonnet, Haiku, Fable) on one identical task. Use when the user asks "which Claude model is best for X", "compare model quality", "Opus vs Sonnet vs Haiku", "model shootout", "benchmark Claude tiers", or "test the models in my subscription". Dispatches one model-pinned subagent per model with an identical frozen prompt, saves each output, then scores objective-first with a blinded-judge fallback and writes a comparison report.
---

# Model Quality Compare

Compare the quality of Claude subscription tiers on a single task, with the experimental
controls that make the comparison trustworthy instead of anecdotal.

## What this is (and is not)

- It **is** an orchestration playbook. ONE skill fans out **one subagent per model**, each
  pinned via the Agent tool's `model` parameter (`opus`/`sonnet`/`haiku`/`fable`).
- It is **not** "one subskill per model." A skill cannot switch the underlying model — only a
  subagent dispatch can. Per-run experiment details are a config file (`spec.yaml`), never a new skill.
- Scope is the **Claude family only**. Subagent model overrides cannot reach GPT/Gemini, so this
  is strictly a within-subscription tier comparison.

## Core principle

Fix the INPUT (a byte-identical frozen prompt + identical context, tools, and system for every
contestant). The only variable allowed is the model. Then measure how the OUTPUTS diverge. You are
not trying to make models produce the same output — you give them the same task and measure quality.

## Phases

```
Phase 0  DESIGN     capture task, freeze the prompt, choose metric + models + trials
Phase 1  SPEC       write output/<date>-<slug>/spec.yaml   (config, NOT a skill)
Phase 2  FAN OUT    dispatch model x trial subagents in parallel, each model-pinned,
                    identical frozen prompt -> output/<exp>/<model>/trial-<n>.<ext>
Phase 3  COLLECT    verify outputs; a refusal / empty / error = a recorded failed trial (it is data)
Phase 4  SCORE      objective check (ground truth) first; blinded judge subagent for subjective quality
Phase 5  REPORT     aggregate.py -> output/<exp>/report.md
```

## Phase 0 — Design the experiment

Establish, and confirm with the user if any are unclear:

1. **Task** — the exact instruction the models must fulfill.
2. **Frozen prompt** — the final prompt text, identical for every contestant. Freeze it now; do not
   let it drift between dispatches. Include all context inline or as referenced files that every
   contestant reads identically.
3. **Metric** — pick the honest option:
   - **Objective (preferred)** — the task has ground truth: code that must pass tests, an
     exact-match answer, a regex/format check, a length bound. Define the check as a command or
     small script that returns pass/fail (and optionally a number) per output file.
   - **Blinded judge (fallback)** — subjective quality with no ground truth. Use `references/rubric-template.md`.
   - Many tasks support **both**; run both and report both.
4. **Models** — default `[opus, sonnet, haiku]` (add `fable`, or drop tiers, as the user wants).
5. **Trials** — default `3` per model. `n=1` is illustrative only; say so if the user insists on it.
6. **Judge model** — fixed, default `sonnet`. If the judge is also a contestant, the report must
   flag self-preference bias.

## Phase 1 — Write the spec

Create `output/<YYYY-MM-DD>-<slug>/spec.yaml`. This is the reproducibility artifact. Example:

```yaml
name: is-prime-shootout
date: 2026-07-01
models: [opus, sonnet, haiku]
trials: 3
metric:
  type: both            # objective | judge | both
  objective: "python3 check.py <output_file>  # exit 0 = pass"
  judge_model: sonnet
  rubric: references/rubric-template.md
frozen_prompt: |
  Write a Python file containing ONLY a function `is_prime(n: int) -> bool`.
  No prose, no markdown fences, no example usage, no prints. Output valid Python only.
output_ext: py
```

## Phase 2 — Fan out (parallel, model-pinned)

For each `model x trial`, dispatch a subagent **in parallel** (multiple Agent calls in a single
message, or `run_in_background`). Every contestant gets:

- `model: <the tier under test>` — this is the ONLY thing that differs between contestants.
- The **identical frozen prompt**, plus this instruction:
  `Write ONLY your final deliverable to output/<exp>/<model>/trial-<n>.<ext>. Do not read other
  trials or outputs. Do not explain.`
- The **same tool access and system framing** for every contestant (no per-model hints), or the
  comparison is confounded.

Record wall-clock latency per dispatch if you can (a secondary metric, not primary quality).

### Alternative Phase 2: API-backed runner (version-pinned)

The subagent `model` aliases (`opus`/`sonnet`/`haiku`/`fable`) each resolve to exactly ONE current
model, so they **cannot** compare two versions of the same tier (e.g. Sonnet 4.6 vs Sonnet 5). When
the experiment needs specific version IDs, use `scripts/api_runner.py` instead of subagent fan-out:

- It calls the Anthropic API directly with **pinned model IDs**, so it spends **metered API tokens,
  not the subscription**. Requires `ANTHROPIC_API_KEY` (from the env or fetched from GSM per the
  user's setup). Install the official SDK first: `pip install anthropic` (verify it's the real
  `anthropic` package before installing).
- Write `<exp>/api_spec.json` with pinned IDs, then run `python3 scripts/api_runner.py <exp>`:
  ```json
  {
    "models": [
      {"name": "haiku", "id": "claude-haiku-4-5"},
      {"name": "sonnet46", "id": "claude-sonnet-4-6"},
      {"name": "sonnet5", "id": "claude-sonnet-5"},
      {"name": "opus", "id": "claude-opus-4-8"}
    ],
    "trials": 1,
    "frozen_prompt": "…identical for every contestant…",
    "output_ext": "py",
    "max_tokens": 1024
  }
  ```
- It disables thinking for every contestant (fair comparison; falls back if a model rejects the
  flag), writes each output to `<exp>/<name>/trial-<n>.<ext>` (same layout Phases 3–5 expect), and
  records latency + token usage in `<exp>/runs.json`. Collection, objective scoring, blinded
  judging, and reporting are identical to the subagent path from here on.

## Phase 3 — Collect

Confirm every expected `output/<exp>/<model>/trial-<n>.<ext>` exists and is non-empty. A model that
refuses, errors, or emits an empty/malformed file **counts as a failed trial for that model** — that
is a real quality signal, not a reason to abort. Continue with whatever succeeded.

## Phase 4 — Score

**Objective path.** Run the defined check against each output file. Write results to
`output/<exp>/objective.json`:

```json
[{"model": "opus", "trial": "1", "passed": true, "detail": "9/9 cases"}]
```

**Blinded judge path.** Never let the judge see which model wrote what.

1. `python3 scripts/anonymize.py output/<exp> --seed 42`
   Shuffles all trial outputs into `output/<exp>/_judge/output_<LABEL>.<ext>` and writes
   `_judge/mapping.json` (label -> model/trial). **The mapping is withheld from the judge.**
2. Dispatch ONE judge subagent, `model: <judge_model>`, told to read ONLY
   `output/<exp>/_judge/output_*.<ext>` (never `mapping.json`), score each against the rubric, and
   write `output/<exp>/_judge/scores.json` keyed by label:
   ```json
   {"A": {"correctness": 5, "clarity": 4, "robustness": 3}, "B": {...}}
   ```

## Phase 5 — Report

`python3 scripts/aggregate.py output/<exp>`

De-anonymizes judge scores via `mapping.json`, merges objective results, and writes
`output/<exp>/report.md`: a per-model scorecard (mean ± sd across trials), per-trial detail, and a
mandatory caveats section. Present the report to the user. Never report a single bare scalar.

## Bias mitigations (non-negotiable)

- Identical frozen prompt, tools, and system for every contestant — model is the only variable.
- Blind + shuffle outputs before judging; the label->model mapping is withheld from the judge.
- Fixed judge model; flag self-preference in the report when the judge is also a contestant.
- Report variance across trials, not just a mean. Treat gaps smaller than the spread as noise.
- Objective ground truth outranks judge opinion. Label judge scores as opinion.

## Error handling

- Contestant refusal / error / empty output -> recorded failed trial, experiment continues.
- Judge cannot parse an output -> mark unscored, note in report.
- Timestamped `<date>-<slug>` experiment dir prevents output collisions.

## Cost note

Runs = models x trials (+1 judge). Defaults = 3 x 3 + 1 = 10 subagent runs. Opus burns
subscription quota fastest. Warn the user before large sweeps.
