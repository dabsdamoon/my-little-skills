# Analytique Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `analytique` skill — a multi-lens analyst that critiques ideas, opinions, plans, and claims with direct, honest, structured assessments.

**Architecture:** Pure prompt-based skill living in a new `analysis-skills` plugin. No scripts, references, or assets — just a SKILL.md with frontmatter and prompt instructions. Registered via plugin.json and marketplace.json.

**Tech Stack:** Markdown (SKILL.md), JSON (plugin.json, marketplace.json)

**Spec:** `docs/superpowers/specs/2026-03-18-analytique-design.md`

---

### Task 1: Create the analysis-skills plugin structure

**Files:**
- Create: `plugins/analysis-skills/.claude-plugin/plugin.json`

- [ ] **Step 1: Create plugin directory structure**

```bash
mkdir -p plugins/analysis-skills/.claude-plugin
mkdir -p plugins/analysis-skills/skills/analytique
```

- [ ] **Step 2: Write plugin.json**

Create `plugins/analysis-skills/.claude-plugin/plugin.json`:

```json
{
  "name": "analysis-skills",
  "description": "Critical thinking and analysis: idea critique, assumption challenging, and fact-checking",
  "version": "1.0.0",
  "author": {
    "name": "dabsdamoon"
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add plugins/analysis-skills/.claude-plugin/plugin.json
git commit -m "feat(analysis-skills): add plugin structure"
```

---

### Task 2: Write the analytique SKILL.md

**Files:**
- Create: `plugins/analysis-skills/skills/analytique/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Create `plugins/analysis-skills/skills/analytique/SKILL.md` with the full skill content. The file must include:

**Frontmatter:**
```yaml
---
name: analytique
description: Analyze and critique ideas, opinions, plans, or claims. Use when asked to criticize, poke holes, fact-check, challenge assumptions, assess feasibility, or evaluate whether an idea is sound.
---
```

**Body content must cover (refer to spec for full details):**

1. **Purpose statement** — one-liner explaining what the skill does
2. **Multi-Lens Analysis Framework** — the 6 lenses table (Logical Consistency, Practical Feasibility, Hidden Assumptions, Second-Order Effects, Alternative Framing, Prior Art). State that 2-3 lenses total are applied: Hidden Assumptions always + 1-2 more auto-selected based on input type.
3. **Process Flow** — the 5 steps:
   - Intent Extraction (restate in one sentence, re-extract if corrected)
   - Lens Selection (auto-select, state which and why)
   - Analysis (apply each lens, deliver findings directly)
   - Verdict (bottom-line assessment, single most important thing)
   - Follow-up Offer (dig deeper options: same lens deeper, new lens, free-form)
4. **Tone & Style rules** — direct/blunt, assertive judgments, evidence-backed, concise, flexible formatting within steps
5. **Scope** — what it IS for (opinions, plans, strategic decisions, ideation, fact-checking) and what it is NOT for (code review, debugging, implementation planning)

- [ ] **Step 2: Verify SKILL.md is under 500 lines**

```bash
wc -l plugins/analysis-skills/skills/analytique/SKILL.md
```

Expected: well under 500 lines.

- [ ] **Step 3: Commit**

```bash
git add plugins/analysis-skills/skills/analytique/SKILL.md
git commit -m "feat(analytique): add SKILL.md with multi-lens analysis framework"
```

---

### Task 3: Register the plugin in marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Add analysis-skills plugin entry**

Add the following entry to the `plugins` array in `.claude-plugin/marketplace.json`:

```json
{
  "name": "analysis-skills",
  "description": "Critical thinking and analysis: idea critique, assumption challenging, and fact-checking",
  "source": "./plugins/analysis-skills"
}
```

- [ ] **Step 2: Verify marketplace.json is valid JSON**

```bash
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('Valid JSON')"
```

Expected: `Valid JSON`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(marketplace): register analysis-skills plugin"
```

---

### Task 4: Test the skill

- [ ] **Step 1: Verify skill is discoverable**

Start a new Claude Code session in the repo and check that `/analytique` appears as a slash command, or that the skill triggers when saying "analyze and criticize".

- [ ] **Step 2: Test with a sample input**

Run `/analytique` with a test statement like: "I think monorepos are always better than polyrepos for team productivity."

Verify the output:
- Restates the intent in one sentence
- States which lenses were selected and why
- Applies each lens with direct findings
- Delivers a verdict
- Offers to dig deeper

- [ ] **Step 3: Test with a plan input**

Run `/analytique` with: "We should rewrite our Python backend in Rust for better performance."

Verify the lenses selected are different from the opinion test (e.g., Practical Feasibility should appear).

- [ ] **Step 4: Test with a fact-checking input**

Run `/analytique` with: "PostgreSQL is always faster than MySQL for read-heavy workloads."

Verify the skill handles fact-checking/research scope appropriately.
