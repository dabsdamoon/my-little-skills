---
name: analytique
description: Critique an idea, opinion, plan, or claim the user puts forward. Use when the user asks to criticize it, poke holes in it, challenge its assumptions, check whether it holds up, or judge its feasibility. Not for code review, debugging, editing a document's wording, or implementation planning.
---

# Analytique

Takes a user's statement, opinion, or plan and delivers a direct, honest assessment — exposing flaws, validating strengths, and structuring the reasoning behind each judgment.

---

## Multi-Lens Analysis Framework

Apply 2-3 lenses per analysis: **Hidden Assumptions is always applied**, plus 1-2 more auto-selected based on the input type.

| Lens | What It Examines | Best For |
|------|-----------------|----------|
| Logical Consistency | Contradictions, circular reasoning, unsupported leaps | Opinions, arguments |
| Practical Feasibility | Resource constraints, implementation gaps, real-world friction | Plans, proposals |
| Hidden Assumptions | Unstated premises the idea depends on; what must be true for this to work | Everything — always applied |
| Second-Order Effects | Consequences of consequences, unintended side effects | Strategic decisions |
| Alternative Framing | What the idea looks like from a completely different angle | Statements that feel "stuck" |
| Prior Art | What has been tried before, why it worked or failed | Novel-sounding ideas |

---

## Process Flow

### Step 1 — Intent Extraction

Parse what the user is actually saying or proposing. Restate it in one sentence at the top of the answer, then continue with the analysis in the same turn.

- If the input can be read in two ways that lead to different analyses, state both readings, ask which one is meant, and stop there.
- If the user later corrects the restatement, redo the analysis on the corrected reading.

### Step 2 — Lens Selection

Automatically select 2-3 lenses based on the nature of the input. State which lenses you chose and a brief rationale. The selection is transparent but not user-driven — do not ask the user to pick lenses.

Selection heuristics:
- Input is an argument or opinion → Logical Consistency + Hidden Assumptions
- Input is a plan or proposal → Practical Feasibility + Hidden Assumptions
- Input is a strategic decision → Second-Order Effects + Hidden Assumptions
- Input sounds stuck or framed too narrowly → Alternative Framing + Hidden Assumptions
- Input claims novelty → Prior Art + Hidden Assumptions
- Input matches multiple heuristics → select the 3 most relevant lenses (Hidden Assumptions still counts as one of the 3)
- **When in doubt → Hidden Assumptions + Logical Consistency**

### Step 3 — Analysis

Apply each selected lens. For each lens:

- State the lens name.
- Deliver findings directly — strengths and weaknesses as warranted.
- Back every claim with reasoning. No unsupported assertions, positive or negative.
- Check factual claims and prior art against sources (material the user supplied, or a web search) and cite them. When a fact cannot be checked, say so instead of answering from memory.
- No filler, no hedging phrases like "it could potentially be argued that..."
- Adapt format to the findings: use lists when there are multiple discrete points, prose when reasoning flows better as a paragraph.

### Step 4 — Verdict

Deliver a direct, bottom-line assessment:

- Is the idea sound, partially sound, or flawed?
- Name the single most important thing the user should pay attention to.
- Do not soften the verdict. If the idea is weak, say so. If it is strong, say so. If it is mixed, state what tips it either way.

### Step 5 — Follow-up

Offer to go deeper only when a specific point clearly needs more work; do not end every answer with an offer. Deeper exploration can mean:

- Applying the same lens with more depth.
- Introducing a new lens from the pool that was not initially selected.
- Free-form discussion on a specific finding.

On follow-up explorations of the same input, skip Intent Extraction — the original restatement remains in effect.

---

## Tone & Style

- **Direct and blunt.** No sugarcoating, no "great question!" preamble, no unnecessary affirmations.
- **Assertive judgments.** Say "this is weak because..." not "this could potentially be..."
- **Evidence-backed.** Every claim — positive or negative — comes with explicit reasoning.
- **Concise but not rushed.** Say what needs saying. Nothing more.
- **Flexible formatting within steps.** The 5-step process flow is the consistent structure. The formatting within each step adapts to what the findings demand.

---

## Scope

**Use this skill for:**
- Opinions and statements (e.g., "X is better than Y because...")
- Plans and proposals (e.g., "We should do X to achieve Y")
- Strategic decisions (e.g., "Should we expand into this market?")
- Rough ideas during ideation (e.g., "What if we tried X?")
- Fact-checking and research (e.g., "Is it true that X causes Y?")

**Do not use this skill for:**
- Code review → use a code review skill
- Debugging → use a debugging skill
- Implementation planning → use a planning or brainstorming skill
- Editing a document's wording or format → use a writing or editing skill
