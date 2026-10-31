---
name: frontend-design
description: Use when creating or visually redesigning web interfaces, interactive prototypes, or screen layouts, especially when design alternatives are requested or previous results feel templated.
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

When novelty is requested, compare the final recommendation with available prior designs and named references. Explain a useful task-specific difference; structural distance alone is not creative quality.

Separate **requirements** from **design hypotheses**. Required information, actions, brand rules, and accessibility constraints can remain constant across candidates. A previous layout, poetic headline, or first-generated component is a hypothesis until the user adopts it. A recommendation may be implemented under existing authorization without being described as user-approved.

Extract useful principles from references: attention hierarchy, density, spatial relationships, feedback, and input reach. A reference need not become a template for the same palette or component arrangement. For a task screen or game HUD, begin with the controls and information needed during use; a promotional introduction belongs only where it serves the task.

## Make deliberate visual choices

- **Structure:** encode priorities through grouping, adjacency, area, alignment, and disclosure. Explain how the chosen organization supports the task. A hero, card grid, or sidebar earns its place through that explanation.
- **Type:** use a legible scale, intentional weights, and fonts that cover the content's languages. One family can suffice. Preserve an existing brand font; unusual type is optional.
- **Color and material:** derive a coherent palette from the subject, with usable contrast and quiet space for important states. Existing brand choices outrank generic aesthetic preferences.
- **Copy:** name actions and states plainly and consistently. Labels, numbers, borders, and decorative headings should communicate something true. Empty and error states guide the next action.
- **Motion:** make changes and consequences understandable. Use automatic motion sparingly and respect reduced-motion preferences.

Check habitual treatments against the brief: tracked uppercase eyebrows, emotional slogans, uniform cards, monospace data chrome, and fashionable light or dark palettes are choices, not defaults or universal bans. Familiar conventions are useful when they make an action easier to recognize.

## Build and inspect

Use the project's stack and reusable components. Match implementation effort to the chosen design. Exercise actual content and important states, including loading, empty, error, selected, disabled, and unavailable where relevant. Keep responsive behavior, keyboard focus, touch targets, and readable contrast intact.

Inspect rendered results at relevant sizes when rendering tools are available. Distinguish code inspection, interaction checks, visual observation, and user preference; none substitutes for the others. State unavailable checks honestly. A static mockup does not establish gameplay readability or usability in motion.

## Deliver and hand off

Explain the useful tradeoff and identify the chosen direction as a recommendation or an adopted decision. In a downstream brief, separate required behavior, selected implementation choices, unresolved alternatives, and unverified assumptions. Carry forward the user's decisions without turning incidental prototype positions or styling into universal constraints.

Preserve source attribution and local adaptations in [NOTICE.md](NOTICE.md).
