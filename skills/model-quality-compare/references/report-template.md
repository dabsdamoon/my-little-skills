# Model Quality Comparison Report — <experiment name>

Task: <one-line task description>
Models: <list>  |  Trials per model: <n>  |  Judge: <model or "none (objective only)">

## Objective results

| Model | Pass rate | Trials |
|---|---|---|
| ... | ... | ... |

## Blinded judge scores

| Model | <dim> (mean±sd) | ... | overall |
|---|---|---|---|
| ... | ... | ... | ... |

Judge scores are model opinion, not ground truth.

## Verdict

<Which model to pick and why. State the trade-off — e.g. Haiku matched Sonnet on correctness at
lower quota cost — rather than a single winner. If the gap is within trial-to-trial spread, say the
tiers are indistinguishable for this task.>

## Caveats

- Non-determinism: outputs vary run to run; gaps smaller than the spread are noise.
- Judge is a single model; if it is also a contestant, self-preference may inflate its own score.
- Objective checks are ground truth; judge scores are opinion.
- n=<trials> per model — <"illustrative only" if n=1 | "modest signal" otherwise>.
