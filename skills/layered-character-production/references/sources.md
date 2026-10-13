# Sources and maintenance scope

This project adapter was assembled on 2026-10-12 for Project MagicGirlSquad's `image designers` workflow. It synthesizes reusable upstream guidance with the current project contracts. It adds no image model, renderer, CLI harness, or paid-service dependency.

## Upstream skills

Reviewed revision: `8c85352d5d75d4dcbe58480bd138e37b9742bab1` of [calesthio/generative-media-skills](https://github.com/calesthio/generative-media-skills).

- [character-design-continuity](https://github.com/calesthio/generative-media-skills/blob/8c85352d5d75d4dcbe58480bd138e37b9742bab1/skills/production/creative-direction/character-design-continuity/SKILL.md): locked versus variable identity, reference roles, state continuity, and final-output review.
- [2d-character-rig-animation](https://github.com/calesthio/generative-media-skills/blob/8c85352d5d75d4dcbe58480bd138e37b9742bab1/skills/production/creative-direction/2d-character-rig-animation/SKILL.md): part responsibilities, pivots and hierarchy, independent draw order, contact/loop inspection, and reproducible frame state.

The upstream skills can be installed separately. Their full manuals and evaluator answer keys are not bundled here. The necessary project workflow is self-contained; optional upstream reading should be selected for the current task. The upstream MIT notice is included in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Project sources inspected

Resolve these in the intended game checkout, not relative to this skill:

- `AGENTS.md`
- `docs/art/CHARACTER-ANIMATION-HARNESS.md`
- `docs/art/CHARACTER-LAYER-AUTHORING.md`
- `docs/art/ADELA-DAMAGE-CONTINUITY-AUDIT.md`
- `docs/art/ADELA-LAYER-WALK-V11.md`
- `docs/art/ADELA-LAYER-DAMAGE-V12.md`
- `data/art/layer_costume_profile.json`
- `tools/character_animation.py`, `tools/layer_costume.py`, `tools/adela_layer_walk.py`, and `tools/adela_layer_damage.py`
- `docs/art/ART-EVALUATION-METRICS.md`, `tools/art_metrics.py`, and `tools/image_checks.py` (added 2026-10-13: generation-time checks, depth-order gates, and review handling)

Project numbers, character bindings, and version examples are dated observations, not defaults for every character. Re-read current local contracts before work. Keep reference provenance, technical validation, observed visual review, user feedback, and runtime installation distinct when updating this adapter.
