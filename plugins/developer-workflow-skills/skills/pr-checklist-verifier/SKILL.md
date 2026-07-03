---
name: pr-checklist-verifier
description: Verifies the unchecked items in a pull request's testing checklist by actually running the appropriate tool (browser/webapp-testing for UI behavior, the test suite for "tests pass", curl for endpoints, a build for "compiles"), then closes the loop by updating the PR body — ticking only the items it proved and recording the evidence. Use this whenever someone asks to "verify the PR checklist", "check off the test plan", "confirm the manual QA items", "verify and update the PR", or runs QA against a PR and wants the description brought up to date. Reach for it any time a PR has `- [ ]` checklist items that ought to be confirmed before merge, even if the user only says "make sure the PR is actually tested."
argument-hint: [pr-number]
model: sonnet
---

# PR Checklist Verifier

Turn a PR's testing checklist from a list of intentions into a list of *confirmed facts* — and make the PR description reflect reality.

A PR checklist is a promise to the reviewer. Items left as `- [ ]` say "someone still needs to confirm this." The failure mode this skill exists to prevent has two halves:

1. **Verifying without recording.** You run the browser test, it passes — and then you move on without updating the PR. The reviewer still sees an unchecked box and has to redo the work or merge on faith. Verification that doesn't reach the PR description is wasted.
2. **Recording without verifying.** Ticking a box because it *probably* works. A checkmark is a claim to the reviewer that you confirmed something. An unbacked checkmark is worse than an empty box — it actively misleads.

This skill does both halves correctly: verify with real evidence, then update the PR — and **only** tick what you actually proved.

## The loop

```
resolve PR → parse checklist → classify each unchecked item →
verify (right tool per item) → honesty gate → update PR body → report
```

Work the unchecked items only. Never touch already-checked items or any non-checklist prose in the body.

---

## Step 1 — Resolve the PR

If a PR number was given as an argument, use it. Otherwise resolve the PR for the current branch:

```bash
gh pr view --json number,title,url,body,headRefName,baseRefName
```

If there's no PR for the current branch, stop and say so — there's nothing to update. (Offer to create one with the pr-creator skill if that seems to be the intent.)

Keep the raw `body` verbatim. You will edit it surgically and write it back; do not regenerate it from scratch.

## Step 2 — Parse the checklist

Find GitHub task-list items in the body — lines matching `- [ ]` (unchecked) or `- [x]` (checked), allowing leading indentation. Split into:

- **Already checked** (`- [x]`) — leave exactly as-is. Don't re-verify, don't reword.
- **Unchecked** (`- [ ]`) — your work queue.

If there are zero unchecked items, report that the checklist is already complete and stop. Don't invent work.

## Step 3 — Classify each unchecked item

Read each unchecked item and decide *how* it could be proven. The item text is freeform English written by a human; use judgment, not keyword matching. Typical mappings:

| Item looks like… | Verify with |
|---|---|
| UI/visual/responsive/interaction behavior ("tab strip scrolls on mobile", "modal closes on Esc", "form shows error state") | the **webapp-testing** skill — drive a real browser with Playwright |
| "tests pass", "unit suite green", "no regressions" | run the project's test runner (`pytest`, `npm test`, `go test`, …) |
| "type-checks", "builds", "compiles", "lint clean" | run the build/typecheck/lint command |
| endpoint/API behavior ("returns 200", "category filter works", "auth rejected") | `curl` / an HTTP client against the running or deployed service |
| data/migration/file-shape claims ("column added", "rows backfilled") | query the DB or inspect the file directly |
| subjective or human-only ("PM signed off", "copy reads well", "looks on-brand", "stakeholder approved") | **cannot self-verify** — these stay unchecked (see honesty gate) |

When an item is browser-shaped, **invoke the webapp-testing skill** and follow it — including its Step 0 auth resolution. Don't reinvent browser plumbing here; that skill already encodes how to stand up a server, inject sessions, and assert DOM state. This skill's job is orchestration + the PR update, not re-implementing QA.

If an item bundles several claims ("tabs work and persist across reload"), verify each sub-claim; the item only gets ticked if *all* of them pass.

## Step 4 — Verify, gathering evidence

For each verifiable item, run the method and capture concrete evidence:

- The command(s) run and their key output (pass counts, HTTP status, measured values).
- For browser checks: the assertion results and screenshot paths.
- A one-line pass/fail verdict.

A verification has exactly three outcomes:

- **PASS** — proven with evidence. Eligible to be ticked.
- **FAIL** — you ran the check and it did *not* hold. This is a **finding**, not a skip. Leave the box unchecked, and surface it prominently — the PR may have a real bug. Mirror the webapp-testing philosophy: report the discrepancy, never quietly adapt the test until it passes.
- **BLOCKED / UNVERIFIABLE** — you couldn't run it (missing creds, no server, item is subjective). Leave unchecked, record why.

## Step 5 — Honesty gate

Before touching the PR, apply the rule that makes the checkmarks trustworthy:

> **Tick a box only for items with a PASS and real evidence behind it. Everything else stays unchecked.**

No "probably fine," no ticking a FAIL because the fix seems easy, no checking a subjective item because you have an opinion. If you wouldn't stake the reviewer's trust on it, don't check it. When in doubt, leave it unchecked and explain in the report — an honest "couldn't verify X" is far more useful than a false green check.

## Step 6 — Update the PR body

This is the half people skip. Always do it when at least one item passed.

1. Flip `- [ ]` → `- [x]` for each PASSED item — and **only** those. Match the exact item text so you flip the right line.
2. Optionally append a short evidence note to the ticked line itself (e.g. `— Playwright 320/375/414px, single-row + scrolls`), keeping it terse.
3. Add or update a `## QA Verification` section near the testing checklist documenting, per verified item: the method, key evidence/metrics, and verdict. Include FAIL and BLOCKED items here too so the reviewer sees the full picture.

Use the bundled helper to do the body edit deterministically and **idempotently** (re-running must not double-tick or stack duplicate QA sections):

```bash
python scripts/update_pr_checklist.py \
  --body-file /tmp/pr_body_current.md \
  --check "Visual QA of the tab strip on mobile widths" \
  --check "Confirm category persistence across a full page reload" \
  --qa-section-file /tmp/qa_verification.md \
  --out /tmp/pr_body_new.md
```

The script flips only the lines whose text contains a `--check` string, replaces (not appends) any existing `## QA Verification` section with the new one, and leaves everything else byte-for-byte. Read its `--help` before first use. Then push the result:

```bash
gh pr edit <number> --body-file /tmp/pr_body_new.md
```

Diff the before/after locally first if the body is large, so you can confirm only the intended lines moved.

## Step 7 — Report

Tell the user concisely:

- **Ticked (N):** each item + one-line evidence.
- **Failed (N):** each item + what broke — call these out; they may block merge.
- **Blocked/Skipped (N):** each item + why it couldn't be auto-verified (so the human knows what's left for them).
- The PR URL.

If nothing could be verified, say so plainly and don't edit the PR.

---

## Principles

- **Close the loop or it didn't happen.** The deliverable is an updated PR description, not a verification you keep to yourself. If you verified something, the PR must reflect it before you're done.
- **A checkmark is a claim.** Back every one with evidence. The whole value of the checklist collapses if boxes get ticked on vibes.
- **A failed check is a gift.** Finding that "persists across reload" is actually broken is the best possible outcome of running the check — surface it loudly, don't bury it.
- **Touch only what you verified.** Preserve already-checked items, prose, and formatting exactly. Idempotent edits — running twice equals running once.
- **Lean on webapp-testing for browser work.** Don't duplicate its auth/session/DOM machinery; orchestrate it.

## Example

**Input:** PR #19 has:
```
- [x] Frontend unit/type suite green
- [ ] Visual QA of the tab strip on mobile widths (horizontal scroll behavior)
- [ ] Confirm category persistence across a full page reload in-browser
- [ ] PM sign-off on the Korean labels
```

**Process:** Item 2 → webapp-testing at 320/375/414px (PASS). Item 3 → webapp-testing: switch tab, reload, assert active tab (PASS). Item 4 → subjective human approval → BLOCKED.

**Output to PR:** items 2 and 3 flipped to `- [x]` with terse evidence notes; a `## QA Verification` section added with the metrics; item 4 left unchecked.

**Report:**
> Ticked 2/3 verifiable items on [PR #19](url). Mobile scroll: PASS (single-row + horizontal scroll at 320/375/414px). Reload persistence: PASS (소아청소년과 survived reload). Left unchecked: "PM sign-off on Korean labels" — subjective, needs a human.
