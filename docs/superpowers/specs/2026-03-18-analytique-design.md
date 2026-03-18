# Analytique — Design Spec

## Overview

Analytique is a multi-lens analyst skill that takes statements, opinions, plans, claims, or research questions and delivers a direct, honest, structured assessment. It always applies the Hidden Assumptions lens, then auto-selects 1-2 more from a pool of analytical lenses based on context. It delivers a verdict and offers to dig deeper.

**Slash command:** `/analytique`

**Trigger phrases:** "analyze and criticize", "critique this idea", "what's wrong with this", "poke holes in this", "is this a good idea", "challenge this", "assess this plan", "is this claim true", "fact-check this"

## What It Does

Takes a user's statement, opinion, or plan and delivers a direct, honest assessment — exposing flaws, validating strengths, and structuring the reasoning behind each judgment.

## Multi-Lens Analysis Framework

The skill automatically picks 2-3 relevant lenses from a pool based on the input type. Not all lenses apply every time — the skill selects what's most useful. **Hidden Assumptions** is always applied; 1-2 more are selected based on context.

| Lens | What it examines | Best for |
|------|-----------------|----------|
| **Logical Consistency** | Contradictions, circular reasoning, unsupported leaps | Opinions, arguments |
| **Practical Feasibility** | Resource constraints, implementation gaps, real-world friction | Plans, proposals |
| **Hidden Assumptions** | Unstated premises the idea depends on, what must be true for this to work | Everything (always applied) |
| **Second-Order Effects** | Consequences of consequences, unintended side effects | Strategic decisions |
| **Alternative Framing** | What the idea looks like from a completely different angle | Statements that feel "stuck" |
| **Prior Art** | What has been tried before, why it worked or failed | Novel-sounding ideas |

## Process Flow

1. **Intent Extraction** — Parse what the user is actually saying/proposing. Restate it back in one sentence to confirm understanding. If the user corrects the restatement, re-extract and restate before proceeding.

2. **Lens Selection** — The agent automatically selects 2-3 lenses based on the nature of the input. It states which lenses it chose and a brief rationale, so the selection is transparent but not user-driven.

3. **Analysis** — Apply each lens. For each, deliver findings directly — strengths and weaknesses. No filler, no hedging. Adapt the format to what the findings demand (bullets, short paragraphs, whatever communicates best).

4. **Verdict** — A direct, honest bottom-line assessment. Is this idea sound? Partially sound? Flawed? What's the single most important thing the user should pay attention to?

5. **Follow-up Offer** — Ask if the user wants to dig deeper into any specific point. Deeper exploration can mean: applying the same lens with more depth, introducing a new lens from the pool that wasn't initially selected, or free-form discussion on a specific finding.

## Tone & Style

- **Direct and blunt** — no sugarcoating, no "great question!" preamble
- **Assertive judgments** — says "this is weak because..." not "this could potentially be..."
- **Evidence-backed** — every claim (positive or negative) comes with reasoning
- **Concise but not rushed** — says what needs saying, nothing more
- **Flexible formatting within steps** — the 5-step process flow (Intent, Lenses, Analysis, Verdict, Follow-up) is the consistent structure, but the formatting within each step adapts to the findings

## Scope

**What analytique IS for:**
- Opinions and statements ("I think X is better than Y")
- Plans and proposals ("We should migrate to serverless")
- Strategic decisions ("Let's prioritize feature A over B")
- Rough ideas during ideation ("What if we approached it this way?")
- Fact-checking and research ("Is this claim actually true?", "What does the evidence say about X?")

**What analytique is NOT for:**
- Code review (use a code review skill)
- Debugging (use a debugging skill)
- Implementation planning (use a planning/brainstorming skill)

## Implementation Notes

- Skill will live at `skills/analytique/SKILL.md`
- No scripts, references, or assets needed — this is a pure prompt-based skill
- Should be registered in the plugin/marketplace system following existing conventions
- **SKILL.md frontmatter `description` field** should distill the trigger phrases into a single description that covers both what the skill does and when to use it, e.g.: "Analyze and critique ideas, opinions, plans, or claims. Use when asked to criticize, poke holes, fact-check, challenge assumptions, assess feasibility, or evaluate whether an idea is sound."
