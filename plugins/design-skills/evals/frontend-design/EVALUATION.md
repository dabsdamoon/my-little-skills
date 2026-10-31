# frontend-design structural exploration and selection evaluation

Date: 2026-10-31. Scope: [issue #45](https://github.com/dabsdamoon/my-little-skills/issues/45). Decision: **provisional**.

## Procedure and revisions

The [primary brief](brief.md) and [original criteria](rubric.md) were written before editing the skill. Five independent no-history agents received the same two synthetic requests without a design skill, followed by five agents using the initial revised guidance (v1). Each response was limited to 500 words. The author read every complete response.

Independent review then identified a selection gap: comparing candidates did not ensure the final recommendation considered previous results. Issue #45 had also been expanded during the work to explicitly distinguish candidate exploration from novelty-aware selection. V2 adds that comparison and bounded unmet-goal reporting. A [supplemental criterion](rubric-v2.md) was recorded before five fresh v2 runs. A separate five-run old-plugin arm was added on the identical primary brief. The original rubric remains unchanged; the selection criterion was not preregistered for the earlier arms.

Baseline repository commit: `6d2d539007d6c3ab57646d726054ba47e3f68ac1`. The old plugin arm uses its 583-word distribution copy, not the different canonical file. Initial guidance is preserved in commit `87468b2782e630f80d5a7083a66d5fb7e721076a` and [initial-run.json](initial-run.json). Final guidance/input hashes and conditions are in [run.json](run.json). All 23 responses are retained under [samples/](samples/), with word counts and SHA-256 values in [samples.json](samples.json). Stored responses retain all content and normalize trailing blank lines to one final newline.

The four groups are no-guidance 5, old-plugin 5, historical guided-v1 5, final guided-v2 5, plus three separate smoke responses. Agents did not receive rubrics or earlier outputs. These are no-history subagents sharing a parent runtime, not separate model weights or an alternate clean harness. The author was not blinded. The model identifier was not independently recorded; do not infer it from agent names. This evaluation is separate from the 27-run research reported in the updated issue; those data were not rerun or independently verified here.

## Limits found in code review

These limits apply to every observation below. Re-measurement is tracked in [issue #47](https://github.com/dabsdamoon/my-little-skills/issues/47).

- **Possible control contamination.** `brief.md` names no characters, yet Mira/Adela appear in three no-guidance responses (control-1, -3, -4), four old-plugin responses (old-1, -3, -4, -5), two v1 responses and one v2 response. The names match a skill listed in the parent session, so parent context reached the "no-history" subagents. Whether the no-guidance arm could see an installed design skill was not recorded. The no-guidance versus guided contrast is therefore not a clean guidance effect.
- **Cross-run final diversity.** The five old-plugin runs end on five different organizations (instrument panel around the arena, thumb-side portrait cluster, right-side swap paddles, bottom-left roster, lower-right stacked selector). All five v2 runs end on player-following HP with right-side reserves. On the cross-run measure issue #45 targets, this evaluation shows no improvement for v2 and may show a narrowing.
- **Reference preloaded.** Guided runs received `references/structural-exploration.md` directly, including for the narrow edit. The scope table's routing, which should load the reference only for open exploration, was not exercised.
- **Shipped text differs from the evaluated v2.** After code review, v3 restores upstream calibration (generated-page looks, typographic tells, the two-pass plan review with the similar-prompt check, note-keeping, line length, CSS specificity), broadens the trigger description, and removes game-specific and maintainer-only wording from the runtime text. v3 was not re-evaluated.

## Primary observations

| Observable | No guidance, 5 runs | Old plugin, 5 runs | Final v2, 5 runs |
| --- | --- | --- | --- |
| Structural exploration before choosing | One composition each | One main composition each; run 2 briefly contrasts a second structure | Two explicit structural candidates each |
| Local hit-area edit preserves approved visible layout | 5/5 plans | 5/5 plans | 5/5 plans |
| Forces another approval meeting | 0/5 | 0/5 | 0/5 |

[Old run 1](samples/old-1.md) mentions a second theatrical/neon direction without explaining another information organization. [Old run 2](samples/old-2.md) briefly rejects a full-width strip before proposing a compact cluster; this is a genuine structural contrast, not scored as no exploration merely because it is short. The other old responses directly describe one composition. The original no-guidance responses all go straight to a single structure.

The historical v1 runs described 2, 3, 2, 2, 2 structural candidates, but comparison focused on those candidates rather than the old layout. The reviewer identified that distinction before the v2 change. All five final v2 plans explicitly compare their recommendation with the supplied timer-over-three-equal-cards sketch and describe a useful relationship change: active health follows its subject while reserve actions remain separate. They label positions and styling as recommendations and retain the required HP/readiness/cooldown/time/XP/danger/input information in their stated plans.

**Final-selection convergence remains visible:** all five v2 runs recommend a field-local/player-following HP organization. Candidate count is therefore not evidence of diverse final choices across repeated runs. The supplemental criterion verifies an explicit, task-relevant comparison against this brief's supplied baseline; it does not establish broad or cross-run novelty.

Both primary requests are text plans, not implemented behavior. Hit-area geometry, overlap, gameplay readability, contrast and accessibility were not executed or rendered. The author checked scope and stated functional coverage rather than matching a mandatory phrase or template.

## Additional smoke observations

Inputs are in [additional-briefs.md](additional-briefs.md).

- [Film program, v1](samples/heldout-film.md): chronological ledger, venue timetable and title/detail screen; preserves access/capacity/booking information in the plan. This is one non-game smoke response, not generalization evidence.
- [Novelty limits and fixed palettes, v2](samples/novelty-edges.md): recognizes recoloring/mirroring of the same list as insufficient novelty, reports the exhausted budget and unmet goal, and uses the authorized functional fallback. It keeps a separate explicit palette-only request within the approved fixed layout.
- [Changed baseline, v2](samples/selection-shift.md): when the existing prototype already uses player-following HP and lower-right reserves, recommends a consolidated squad rail instead. It explains how comparing HP and selecting a reserve become one action surface. This shows baseline-sensitive selection in one case; it does not establish a novelty success rate.

## Interpretation and remaining work

Within the limits above, the observations support only provisional use of scope routing, explicit structural comparisons, and novelty-aware final-selection reasoning. They do not prove visual originality, better usability, aesthetic quality, statistical significance, or a particular model/harness cause. Repeated palette/instrument language persists. V2 final choices still converge on this primary brief. Explicitly comparing a baseline is a bounded process improvement, not a validated creativity score.

Remaining in issue #45: representative rendered comparisons, automatic skill-selection/installation checks, more domains and repeats, independent quality/functional judgments, comparison-metric validation, and costs/acceptance rates for an external selection procedure. No universal role set, fixed candidate count or distance threshold is imported from the issue's pilot. These guides do not require five-run benchmarks or automatic extra tools for ordinary UI work.

The briefs are synthetic; some responses contain character names that leaked from the parent session (see the limits above). No private customer assets, production data, hidden prompts, credentials or generated images are included. Text samples are evidence, not reusable visual templates. Explicit brand choices, fixed layouts and user-authorized scope retain priority.

## Packaging verification

Run from the repository root:

```sh
python3 plugins/design-skills/evals/check_distribution.py
uv run --with pyyaml python skills/skill-creator/scripts/quick_validate.py skills/frontend-design
uv run --with pyyaml python skills/skill-creator/scripts/quick_validate.py plugins/design-skills/skills/frontend-design
```

The distribution check compares the complete canonical/plugin file trees and public plugin metadata rather than prose phrases. [Recorded fixture outcomes](distribution-checks.json): original main is rejected for a divergent entrypoint and missing Codex manifest; matching revised copies pass; a deliberately stale mirror notice and a mismatched version are rejected. Both original entrypoints already passed frontmatter validation, so schema checks alone did not detect the distribution defect.

Both manifests declare design-skills 1.1.0. Existing Apache licenses are unchanged; [NOTICE](../../../../skills/frontend-design/NOTICE.md) records the reviewed upstream revision and local adaptation. Metadata/directory checks are not end-to-end Codex/Claude installation tests. This PR does not overwrite an installed cache or the skill already loaded in this session. Merge, marketplace refresh, and a new session are separate steps.

## Reproduction

Use a fresh agent for each response, the identical `brief.md`, and only the selected condition's guidance. Supply the exact relevant reference to guided runs, not grading criteria or earlier outputs. Preserve the actual inputs, guidance revision, runtime settings where known, full outputs and grader. Read results for functional and structural meaning; do not use keyword counts or model-assigned novelty probabilities. If future samples change the budget, brief, comparison material or renderer, record a separate condition rather than merging it into these counts.
