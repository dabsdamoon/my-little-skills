# Blinded Judge Rubric (default)

You are scoring anonymized outputs. You do NOT know which model produced which output, and you must
not try to guess. Score each output independently on its own merits.

Read ONLY the files `output_<LABEL>.<ext>` in the `_judge/` directory. Do NOT open `mapping.json`.

For each output, score every dimension on an integer 1-5 scale (5 = best):

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| **correctness** | wrong or broken | mostly works, minor errors | fully correct |
| **instruction_following** | ignores key constraints | follows most | follows every constraint exactly |
| **completeness** | major gaps | covers the essentials | thorough, no gaps |
| **clarity** | confusing / sloppy | readable | clear and well-structured |

Write results to `_judge/scores.json` keyed by label, e.g.:

```json
{
  "A": {"correctness": 5, "instruction_following": 4, "completeness": 5, "clarity": 4},
  "B": {"correctness": 2, "instruction_following": 3, "completeness": 2, "clarity": 3}
}
```

Adapt the dimensions to the task when appropriate (e.g. swap `completeness` for `robustness` on a
code task), but keep the 1-5 integer scale and the JSON-keyed-by-label output format.
