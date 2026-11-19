# Claude subscription comparison on one task

This preserves the original single-task route. It requires a host tool that can
actually pin Claude contestants; Codex subagents cannot be assumed to expose
Claude aliases. Verify current host model IDs rather than guessing aliases.

1. Freeze one prompt, identical supporting context, tools and system framing.
   Define objective ground truth or use [rubric-template.md](rubric-template.md).
2. Record a spec with requested models, task, grader, context hashes, trial count,
   output extension, judge if used, and call budget. Default three trials/model
   on this route; smaller samples are explicitly pilots.
3. Dispatch one fresh model-pinned subagent per model/trial. Give each the same
   prompt and permissions; save its deliverable to
   `<experiment>/<name>/trial-<n>.<ext>`. Prohibit reading other trials. Use sequential
   dispatch if comparing latency, and distinguish harness time from generation speed.
4. Preserve every output/error. Transport/model errors are unavailable with coverage
   shown. Empty/refused/malformed completed responses follow the declared rubric.
5. Run objective checks first and write `objective.json`:

```json
[{"model":"contestant-name","trial":"1","passed":true,"detail":"9/9 cases"}]
```

For subjective quality:

```bash
python3 <skill-dir>/scripts/anonymize.py <experiment> --seed 42
```

Give a fixed judge only `_judge/output_*` plus the rubric, withholding
`_judge/mapping.json`. It writes `_judge/scores.json`, keyed by anonymous labels
and numeric criterion scores. Flag self-preference if the judge is a contestant.
Judge opinions are not objective accuracy.

```bash
python3 <skill-dir>/scripts/aggregate.py <experiment>
```

The legacy aggregator summarizes supplied scored rows. Separately report expected
versus completed trial coverage and unavailable trials; its output alone does not
prove a complete experiment. See [report-template.md](report-template.md) for caveats.

## Explicitly billed legacy API utility

`scripts/api_runner.py` remains an Anthropic API compatibility utility. It cannot
execute GPT models and does not use any subscription. Use only with explicit
authorization for separate API spend. It requires the official `anthropic` SDK,
API credentials and `<experiment>/api_spec.json` with `models` (`name` / `id`),
`trials`, `frozen_prompt`, `output_ext` and `max_tokens`.

This legacy utility may retry rejected thinking settings without those settings.
It therefore does not establish equal reasoning settings. Strict controlled-effort
comparisons require an independently verified adapter. Never select an API route
merely because a requested subscription model is unavailable.
