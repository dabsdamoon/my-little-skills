---
name: layered-character-production
description: "Create, repair, and review Project MagicGirlSquad's layered 2D character artwork and animation harness. Use for Mirinae/Adela character sheets, body and costume parts, fixed-scale rigging, walk cycles, HP costume damage, expression binding, and playable review artifacts. Applies to the image designers workflow; general illustration and unrelated animation projects do not need this project adapter."
license: "MIT; includes guidance adapted from generative-media-skills (see THIRD_PARTY_NOTICES.md)"
---

# Layered Character Production

Turn the current character design into reusable body, costume, expression, and motion assets through the project's existing harness. Preserve character identity across revisions and inspect the actual composed motion before claiming visual completion.

## Resolve the project and the requested result

The chat's working directory may be an image folder while the harness lives in a different Git worktree. Resolve the intended checkout from the user's paths, current artifact, or known worktrees. Confirm `tools/character_animation.py` and `docs/art/CHARACTER-LAYER-AUTHORING.md` exist there. Do not assume the skills repository or this skill's directory is the game project.

Read that checkout's `AGENTS.md`, `docs/art/CHARACTER-ANIMATION-HARNESS.md`, and `docs/art/CHARACTER-LAYER-AUTHORING.md`. Inspect the current character profile, run, latest review, and relevant source images. For game behavior changes, also read the repository's development and design requirements. If the project cannot be located, ask for its path while avoiding guesses that mutate another checkout.

Use the latest user request and the project's current contracts as the authority. The references here describe the harness inspected on 2026-10-12; resolve later changes from the checkout. Existing user authorization carries through routine reversible production steps. A quality checkpoint is an inspection step, not an automatic request for another approval. Record pending aesthetic feedback honestly and continue other authorized work.

Route only the requested work:

| Request | Load | Intended result |
| --- | --- | --- |
| Compare, diagnose, or review | [Review and delivery](references/review-delivery.md) and the relevant production reference | Evidence and a bounded repair plan; no unsolicited regeneration |
| New or revised art, parts, costumes, or expressions | [Harness and continuity](references/harness-continuity.md) | Registered artwork with preserved references and explicit invariants |
| Rig, pose, walk, or damage-state motion | [Rig and costume mechanics](references/rig-costume.md), then review | Connected parts, readable motion, and a playable review artifact |
| Resume after interruption | [Harness and continuity](references/harness-continuity.md) | Recover the current request and returned assets before making another generation call |

The installed `character-design-continuity` and `2d-character-rig-animation` skills can supply broader design or animation guidance when needed. This adapter contains the project essentials and works without those optional installations; do not load both entire skills on every small repair. [Sources and scope](references/sources.md) records the upstream revision and local contracts used.

## Preserve the design before changing its construction

Record a short production brief in the existing run/review conventions:

- Character ID, selected design variant, current source bundle, and requested output.
- Locked features: face, proportions, palette, signature items, asymmetries, camera, body scale, and approved regions.
- Intended changes: the specific garment, damage feature, facial state, pose, or defect.
- Source roles: exact edit target, identity/design reference, previous damage reference, and pose/registration guide.
- Needed parts and unresolved connections, with the current reference and output hashes.

Open the actual reference images. A historically used image is not necessarily user-approved. Preserve useful prior work, but follow an explicit redesign request within its stated scope. Do not silently reset earlier damage designs or expressions when converting a character to layers.

## Build and inspect in dependency order

1. **Register source art.** Reuse the current run and source bundle when compatible. Keep returned PNGs immutable; record generated originals, request IDs, tool/model information, and derived masks/transforms separately. Use the current `imagegen` skill and available image tool for raster generation or repainting. Follow the environment's image-editing rules; programmatic compositing or cropping requires the applicable authorization.
2. **Prepare complete parts.** Separate covered body, torso garments, left/right sleeves, lower garment, accessories, and moving limb segments by their motion and occlusion responsibilities. Reconstruct hidden connections and leave overlap around joints. A garment-off view must reveal the intended underlying part, not a hole or a fragment baked into another layer.
3. **Register and bind.** Keep the body canvas, scale, and anatomical landmarks stable. A generated atlas may need a newly inspected part-to-rig mapping; record the mapping rather than scaling each whole character to its visible bounds. Keep transform hierarchy distinct from front/back draw order.
4. **Inspect key poses before expanding.** Review rear, side, and front arm positions, plus contact and passing poses for walking. Check seams, silhouette, volume, hand/cloth order, and protected regions on composed images. Fix the source connection or rig when that is the cause, instead of repainting every frame.
5. **Build the requested motion and states.** Retain the current run's timing and camera. Add secondary cloth/hair motion after contacts and primary poses work. Costume damage, current-HP expression, and hit-reaction animation are separate outputs; implement and report only those actually requested and created.
6. **Review the deliverable.** Use [Review and delivery](references/review-delivery.md) for technical checks, reference comparison, real playback, and the finished artifact path. Apply the same review to affected outputs after changing a source or contract.

For a narrow repair, enter at the affected step and recheck its dependents. A new full production follows the dependency order without restarting already accepted work.

## Completion means evidence for the requested scope

Report separately: files built, technical checks performed, design observations, browser/playback observations, user aesthetic acceptance, and game integration. Reuse existing status fields rather than inventing a parallel harness schema.

An HTML file existing, an audit command exiting successfully, or thousands of passing assertions does not establish that the artwork looks right or the page plays. An unobserved check remains unverified. If the current brief asks for a moving artifact, deliver the built page and its assets, inspect playback where supported, and state any access limitation.

When a defect reveals a missing reusable production rule and harness improvement is in scope, update the project's contract and the corresponding observable check together. Read the project's `refactoring-resistant-tests` skill before writing or changing automated tests. Keep game installation within the user's authorized scope and the delivery format's actual support.
