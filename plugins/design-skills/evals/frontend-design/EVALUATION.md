# frontend-design structural exploration evaluation

Date: 2026-10-31. Scope: [issue #45](https://github.com/dabsdamoon/my-little-skills/issues/45). Decision: **provisional**.

## Question and procedure

Does the revised guidance make an agent compare usable structural candidates and distinguish requirements from recommendations, without expanding an approved local edit?

The [brief](brief.md) and [criteria](rubric.md) were written before modifying the skill. Baseline repository commit: `6d2d539007d6c3ab57646d726054ba47e3f68ac1`; exact guidance and input hashes are in [run.json](run.json). Five independent, no-conversation-history agents received the same two synthetic requests with no design skill; five new agents then received the same requests plus the revised skill and its conditional reference. Each was limited to a 500-word text response. They did not receive the grading rubric or previous outputs. The author read every full response. Responses are retained under [samples/](samples/), with sizes and SHA-256 values in [samples.json](samples.json).

These are no-history subagents in the same runtime environment, not isolated model weights or a clean alternate harness. The control is **no design guidance**, not the old packaged skill. The earlier reported single-layout failure motivates the work but is not an extra controlled sample. No claim is made that the revised guidance outperforms the old skill or the latest upstream skill in a head-to-head trial.

## Observations

| Observable | Control runs 1–5 | Revised runs 1–5 |
| --- | --- | --- |
| Structural candidates described before choosing | 1, 1, 1, 1, 1 | 2, 3, 2, 2, 2 |
| Compares at least two structures in request A | 0/5 | 5/5 |
| Local hit-area request preserves approved visible layout | 5/5 | 5/5 |
| Forces another approval meeting | 0/5 | 0/5 |

All control responses went directly to one composition. Four placed reserve actions on the right and one on the left; all used related field-instrument language and pale/sage/ivory styling. For example, [control 2](samples/control-2.md) directs the builder to “deliver one responsive HUD composition.”

All revised responses described distinct organizations before recommending one. [Revised 2](samples/revised-2.md) compares a bottom rail, distributed controls, and a roster column. The responses explicitly identify functional requirements and label placement/styling as recommendations. Their stated plans retain individual HP, active/reserve identity, shared cooldown, time, XP, danger feedback, and input considerations; these behaviors were not implemented or executed.

Both arms preserve the approved search button's visible 36-pixel layout and propose a larger hit region with overlap/clipping checks. This is scope-preservation evidence from plans, not a rendered hit-target test.

A [held-out film-program request](samples/heldout-film.md) produced a chronological ledger, venue timetable and title/detail screen, then recommended one under the existing authorization. It preserves access/capacity/booking information in its plan. This is one non-game smoke sample, not a generalization result.

## Interpretation and limits

The observations support keeping this wording provisionally for low-cost structural exploration and scope routing. They do not establish perceived originality, visual quality, accessibility compliance, gameplay readability, production impact, or statistical significance. The author graded the outputs and was not blinded; no sample-independent judging model was used. Same-brief repetition is narrow coverage.

Related palette and instrument-style language persists across revised runs. Increasing the number of feasible structures is not proof that aesthetic convergence has been solved. Rendered comparisons, additional domains, input modes, and representative users remain future evaluation. There is no validated creativity score or invented generation probability.

No production UI, private customer assets, model/system prompts, or credentials are included. All retained examples are synthetic. The guidance preserves user-specified layouts and preferences; explicit palette-only work remains palette-only work.

## Packaging verification

Run from the repository root:

```sh
python3 plugins/design-skills/evals/check_distribution.py
uv run --with pyyaml python skills/skill-creator/scripts/quick_validate.py skills/frontend-design
uv run --with pyyaml python skills/skill-creator/scripts/quick_validate.py plugins/design-skills/skills/frontend-design
```

The distribution check compares the complete canonical and plugin trees and the public plugin metadata; it does not match prose phrases or headings. [Recorded fixture outcomes](distribution-checks.json): original `origin/main` is rejected for a divergent entrypoint and missing Codex manifest; matching revised copies pass; a deliberately stale mirrored notice and a mismatched manifest version are rejected. The old entrypoints already pass frontmatter validation, showing why schema validation alone did not catch the original distribution problem.

Both manifests declare design-skills 1.1.0. Existing Apache licenses remain unchanged and [the notice](../../../../skills/frontend-design/NOTICE.md) records the upstream revision and local adaptation. Package metadata parsing and directory agreement are not end-to-end Codex/Claude installation tests. Installation/cache refresh is deliberately separate from this PR and follows merge; the current session's loaded skill is not retroactively replaced.

## Reproduce or extend

Use a fresh agent per sample. For the control provide only `brief.md`, prohibit loading design skills, and collect the response without the rubric. For the guided arm add the exact revised `SKILL.md` and only its relevant reference. Preserve actual outputs and document any changed inputs, guidance revision, runtime/model settings if available, and grader. Judge the observable task contract rather than template words. The original run did not record an independently controllable model identifier; do not reconstruct one from agent names.

The minimal reference and existing user authorization determine work size. Do not turn this evaluation into a mandatory five-run benchmark for ordinary UI tasks.
