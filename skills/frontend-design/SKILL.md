---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces. Use when building, restyling, or redesigning web components, pages, artifacts, posters, or applications (websites, landing pages, dashboards, React components, HTML/CSS layouts, interactive prototypes, screen layouts) or when styling or beautifying any web UI. Also use when design alternatives are requested, when previous results feel templated, and when implementing or adjusting an approved design.
license: Complete terms in LICENSE.txt
---

# Frontend Design

Create a working interface whose organization and visual language come from the user's task and subject. Preserve function, accessibility, and explicit preferences while exploring choices the brief leaves open.

## Choose the scope

| Request | Approach |
| --- | --- |
| A local adjustment to an approved interface | Preserve its structure, content, tokens, and interactions. Change and verify the requested property. |
| Implementation of a selected design | Follow that design; resolve only unspecified details. |
| A new composition, open redesign, or request for more variety | Compare low-cost structural candidates before committing to a polished direction. Read [structural exploration](references/structural-exploration.md). |
| Palette, typography, or another explicit variation within a fixed layout | Explore the requested axis while keeping the approved structure. |

Respect the requested deliverable count and existing authorization. Exploration is not a reason to force another approval meeting, produce several complete applications, or expand a small repair.

## Ground the choices

Use the supplied brief, actual content, assets, references, and existing implementation. Identify the audience, primary task, and decisions the interface must support. Ask only for missing information that materially changes the work; otherwise state a reasonable assumption and proceed.

When novelty is requested, compare the final recommendation with available prior designs and named references. When none are supplied, compare it with the default you would produce for any similar brief. Explain a useful task-specific difference; structural distance alone is not creative quality.

Separate **requirements** from **design hypotheses**. Required information, actions, brand rules, and accessibility constraints can remain constant across candidates. A previous layout, poetic headline, or first-generated component is a hypothesis until the user adopts it. A recommendation may be implemented under existing authorization without being described as user-approved.

Identify the problem a reference solves and the principle worth transferring: attention hierarchy, density, spatial relationships, feedback, or input reach. Where choices remain open, derive structure and motion from this task's content and actions. Reuse components and implementation techniques while choosing composition, palette, timing, and sequence for the brief. When the user requests close reproduction or adopts a design, preserve that fidelity.

For a task screen, begin with the controls and information needed during use; a promotional introduction belongs only where it serves the task.

## Make deliberate visual choices

- **Structure:** encode priorities through grouping, adjacency, area, alignment, and disclosure. Explain how the chosen organization supports the task. A hero, card grid, or sidebar earns its place through that explanation.
- **Type:** use a legible scale, intentional weights, and fonts that cover the content's languages. One family can suffice. Preserve an existing brand font; otherwise choose typefaces for this brief rather than the families you would reach for on any project. Keep body lines under about 80 characters; serif body text can run slightly longer with slightly more line-height.
- **Color and material:** derive a coherent palette from the subject, with usable contrast and quiet space for important states. Existing brand choices outrank generic aesthetic preferences.
- **Copy:** name actions and states plainly and consistently. Labels, numbers, borders, and decorative headings should communicate something true. Empty and error states guide the next action.
- **Motion:** make changes and consequences understandable. Review [state and change](#make-state-and-change-understandable) across the user's flow. Use automatic motion sparingly and respect reduced-motion preferences.

Avoid these default typographic treatments; they are the commonest tells of a generated page: accenting a single word or phrase in a headline, all-caps labels, and unnecessary labels above content.

For calibration, generated designs currently cluster around these looks:

1. a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta or warm-clay accent (near #D97757);
2. a near-black background with a single bright acid-green or vermilion accent;
3. a broadsheet layout with hairline rules, zero border-radius, and dense newspaper-like columns;
4. the SaaS card kit: identical rounded cards, one radius and one soft grey shadow on everything, and gradient washes as decoration;
5. template chrome regardless of subject: a tracked ALL-CAPS eyebrow above every heading, meta strings joined with middle dots, 'WORD — fragment' labels, tinted near-black standing in for black, monospace for small data labels, and '→' appended to link and button text.

Each is legitimate for some briefs, but they are defaults rather than choices. Where the brief or brand pins down a direction, follow it exactly, including when it asks for one of these looks. Where it leaves an axis free, do not spend that freedom on one of these defaults. Familiar conventions remain useful when they make an action easier to recognize.

## Plan, then review against the brief

For a new composition or redesign, write a compact plan before polished code: 4–6 named hex values, the typefaces and their roles, a layout concept as a sentence or ASCII wireframe with alignment guidance, and the principles that make this design specific. In an open exploration, the structural candidates are the layout part of this plan.

Review the plan before building. If any part reads like the default you would produce for any similar brief (work through a similar prompt and see whether you arrive somewhere similar), revise it and say what changed and why. If you can keep notes across passes or sessions, record what you tried so later work does not repeat it.

## Make state and change understandable

Trace the user's flow through consequential state changes and the intervals between them, including changes without direct input. Identify what the user must understand to interpret their actions, recognize the current situation, and decide what to do next. Where the interface leaves them guessing, provide timely feedback grounded in the available system state.

Choose motion when its temporal behavior makes causality, continuity, or ongoing activity clearer than a static update. Use static feedback where it communicates enough. For functional motion, ask what useful understanding would be lost if it were removed. Do not imply progress or completion unsupported by the available evidence.

Acknowledge input promptly and distinguish receipt from confirmation of its outcome. Use timing to make dependencies between related changes legible within the project's motion language. Preserve unchanged context and the identity of objects as their state changes. For supported interruptions, continue coherently from the current visible state toward the latest valid state. Presentation timing must not delay task feedback; let settled results remain readable.

Verify the flow over time for both missing feedback and motion that communicates nothing useful. When reduced motion is requested, preserve the same information without relying on animation.

## Build and inspect

Use the project's stack and reusable components. Match implementation effort to the chosen design. Exercise actual content and important states, including loading, empty, error, selected, disabled, and unavailable where relevant. Keep responsive behavior, keyboard focus, touch targets, and readable contrast intact. Plan CSS selector specificity deliberately; rules such as `.section` and `.cta` can cancel each other's padding and margin.

Inspect rendered results at relevant sizes when rendering tools are available. For motion, watch playback at normal speed from the triggering change through the settled result, including supported interruption and resumption. Use recordings or frame stepping to investigate faults; selected frames cannot establish continuous playback, and geometry checks cannot establish visual quality. Distinguish code inspection, interaction checks, visual observation, and user preference; none substitutes for the others. State what was observed and what remains unverified.

## Deliver and hand off

Explain the useful tradeoff and identify the chosen direction as a recommendation or an adopted decision. In a downstream brief, separate required behavior, selected implementation choices, unresolved alternatives, and unverified assumptions. Carry forward the user's decisions without turning incidental prototype positions or styling into universal constraints.
