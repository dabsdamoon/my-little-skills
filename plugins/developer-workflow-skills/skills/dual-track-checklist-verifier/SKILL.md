---
name: dual-track-checklist-verifier
description: Verifies and ticks off a pull request's unchecked test-plan or checklist items (`- [ ]`) by re-running each check on the PR's current head commit, then updates the PR body with only what it proved and the evidence. Use when asked to verify the PR checklist, check off the test plan, confirm QA items, or verify and update a PR before merge. Handles any PR test plan and dual-track-pr-creator bodies, where automated results never tick customer, usability, or production claims.
argument-hint: [pr-number]
---

# Dual-Track Checklist Verifier

Turn a PR's checklist from a list of intentions into a list of *confirmed facts*, without letting a checkmark claim more than the evidence supports.

A checklist is a promise to the reviewer. `- [ ]` says "someone still needs to confirm this." There are four ways to break that promise:

1. **Verifying without recording.** You run the check, it passes, you move on. The reviewer still sees an empty box and either redoes the work or merges on faith.
2. **Recording without verifying.** Ticking a box because it *probably* works, or because someone said it passed. A checkmark is a claim. An unbacked one is worse than an empty box: it actively misleads.
3. **Recording the wrong kind of proof.** Ticking "users can tell which tab is active" because an automated test asserts an attribute. The box now claims user validation that nobody obtained.
4. **Proving it on the wrong commit.** A green run on an earlier push, or local tests on a tree with unpushed edits, says nothing about what is about to merge.

## Two kinds of body

The same loop handles both. Detect which one you have in Step 2.

| | Generic test plan | Dual-track body |
|---|---|---|
| Written by | `pr-creator`, a PR template, a person | `dual-track-pr-creator` |
| Recognize by | `## Test plan`, `## Testing Checklist`, or another `##` heading naming test/checklist/QA | `**Track:**` header, `## Verification`, an acceptance-traceability table (PASS / FAIL / MISSING), `## Not included / out of scope` |
| Evidence section goes | right after the checklist (helper default) | before `## Not included` (`--before-heading`) |
| Extra work | none | `--audit-table`, then reconcile the table and the out-of-scope list |

Every gate below applies to both. A generic checklist can say "users understand the new error" or "PM approved the copy" too, and those still need a human.

## Relationship to sibling skills

- **`pr-creator`** and **`dual-track-pr-creator`** write the bodies this skill reads. Writing or rewriting a PR description is their job; this skill only flips boxes, rewords the items it ticks, and adds an evidence section.
- **`webapp-testing`** owns browser work: picking the browser tool the session has (Claude in Chrome, Playwright MCP, or its own Playwright scripts), starting the server, and setting up auth. Invoke it for browser-shaped items and follow its routing; do not rebuild that plumbing here. Under Codex, which has its own browser plugin, use that plugin where `webapp-testing` would drive a browser.

This skill is otherwise self-contained. Do not assume another skill can be imported as a runtime dependency.

## The loop

```
resolve PR + pin head SHA → parse checklist → classify each unchecked item →
verify on the head → evidence-kind gate → honesty gate →
reword + tick + record → confirm head unchanged → push → report
```

Work the unchecked items only. Never touch already-checked items or non-checklist prose.

---

## Step 1: Resolve the PR and pin the head

Use a given PR number; otherwise omit it and gh resolves the current branch's PR. Invoke the CLI as `command gh` so a shell alias or function cannot shadow it:

```bash
command gh --version
command gh pr view <n> --json number,title,url,body,headRefName,headRefOid,baseRefName
```

In a clone with several remotes (a fork with an `upstream`), gh can pick the wrong repository: pass `-R OWNER/REPO` to every `gh pr` command.

If there is no PR, stop and say so. Offer `pr-creator` or `dual-track-pr-creator` if creating one seems to be the intent.

Record `headRefOid` as `HEAD_SHA`. Every tick must rest on evidence from that commit.

- **Local runs** (tests, builds, a dev server for browser checks) prove something about the head only when the working tree *is* the head: `git rev-parse HEAD` must equal `HEAD_SHA` and `git status --porcelain` must be empty. If not, do not tick from that tree. Ask before switching branches; `command gh pr checkout <n> --worktree <path>` checks the PR out into a separate worktree and leaves the user's tree alone.
- **Deployed previews** (browser or `curl` against a URL) count only if the deployment was built from `HEAD_SHA`. Confirm the deployment's commit before trusting it.

Save the raw body verbatim. You will edit it surgically; never regenerate it.

```bash
WORK=$(mktemp -d)
command gh pr view <n> --json body --jq .body > "$WORK/body.md"
```

## Step 2: Parse the checklist

Find task-list lines (`- [ ]` / `- [x]`, allowing indentation and `*` bullets). Split into:

- **Already checked**: leave byte-for-byte. Do not re-verify, do not reword.
- **Unchecked**: your work queue.

Zero unchecked items means the checklist is complete. Report that and stop; do not invent work.

Decide which kind of body this is (table above). For a dual-track body, also locate the acceptance-traceability table and `## Not included / out of scope`. Both record status a second time, so a tick can leave them disagreeing with the checklist (Step 7).

## Step 3: Classify each unchecked item

The text is freeform English. Use judgment, not keyword matching.

| Item looks like… | Verify with |
|---|---|
| UI/visual/responsive/interaction behavior | the **webapp-testing** skill, a real browser |
| "tests pass", "suite green", "no regressions" | the project's runner (`pytest`, `npm test`, `go test`) on the head |
| "type-checks", "builds", "compiles", "lint clean" | the build/typecheck/lint command on the head |
| endpoint/API behavior | `curl` or an HTTP client against a service built from the head |
| "CI is green", "checks pass on this PR" | `gh pr checks`, bound to `HEAD_SHA` (below) |
| data/migration/file-shape claims | query the DB or inspect the file |
| "PM signed off", "copy reads well", "looks on-brand" | **cannot self-verify**: human judgment |
| "users can tell / notice / understand …", "screen reader announces …" | **cannot self-verify**: needs a representative user or assistive technology |
| "behaves correctly in production", "no errors after deploy" | **cannot self-verify** before the deploy exists |

If an item bundles claims ("tabs work and persist across reload"), verify each; tick only if all pass.

### CI on the current head

```bash
command gh pr checks <n> --json name,state,bucket --required
```

- `bucket` is `pass`, `fail`, `pending`, `skipping`, or `cancel`. Every required check must be `pass`. A `skipping` check is acceptable only when the workflow is designed to skip on PRs; say which one and why in the evidence.
- Exit code 8 means checks are still pending. The item is BLOCKED, deferred until they finish (or wait with `--watch`).
- If `--required` reports no checks, rerun without it and judge every check, noting that the repo marks none as required. If there are no checks at all, leave the item unchecked and report that the PR has no CI.

`gh pr checks` reads the PR's latest commit but prints no SHA, so bind the result to `HEAD_SHA` explicitly. Spell out `OWNER/REPO`; `gh api` has no `-R` flag and its `{owner}/{repo}` placeholders resolve from the current directory:

```bash
command gh api "repos/OWNER/REPO/commits/$HEAD_SHA/check-runs" --paginate \
  --jq '.check_runs[] | [.name, .head_sha[0:7], .status, .conclusion] | @tsv'
```

Each required check from `gh pr checks` must appear here as `completed` / `success`. Some integrations report commit statuses instead of check runs; read them from `repos/OWNER/REPO/commits/$HEAD_SHA/status` and judge `.statuses[]`, because the combined `.state` reads `pending` when there are no statuses at all.

## Step 4: Verify on the head, gathering evidence

**Re-run, do not relay.** Tick only what you re-ran or observed yourself on `HEAD_SHA` in this session. A user saying "I ran QA and it passed", a bot comment, an old screenshot, or a CI run on an earlier commit is a lead, not evidence. If you cannot re-run an item (no credentials, no server), it stays unchecked; record the report you were given as unconfirmed.

Capture, per item: the commands run and their key output (pass counts, HTTP status, measured values, SHAs), screenshot paths for browser checks, and a one-line verdict.

Four outcomes:

- **PASS**: proven with evidence on the head. Eligible to tick.
- **FAIL**: you ran it and it did not hold. A **finding**, not a skip. Leave unchecked and surface it prominently; the PR may have a real bug. Never quietly adapt the check until it passes.
- **BLOCKED, needs a human**: subjective, or requires a representative user or assistive technology. No amount of tooling closes it.
- **BLOCKED, deferred to an event**: verifiable later but not now without side effects: a deploy has to happen, a tag has to be pushed, CI has to finish. Say which event unblocks it.

Keep the two BLOCKED kinds apart. "Needs a human" is a standing gap in the PR. "Deferred" is a scheduling fact, and a reviewer reads them differently.

**Never manufacture the event to close a box.** Pushing a release tag so a "tag gate works" item can be ticked deploys to production for the sake of a checkmark. Leave it BLOCKED.

## Step 5: Evidence-kind gate

Check that the *kind* of evidence matches the *kind* of claim.

> An automated result may not tick an item that claims customer, usability, or production validation.

| The item claims | An automated pass proves | Verdict |
|---|---|---|
| an attribute/DOM state exists | exactly that | may tick |
| a user can perceive or understand something | nothing about perception | BLOCKED, needs a human |
| a screen reader announces something | that the attribute is present, not that it is announced | BLOCKED, needs a human |
| behavior in production | nothing until deployed | BLOCKED, deferred |
| a stakeholder approved | nothing | BLOCKED, needs a human |

When an item mixes both ("`aria-current` is set **and** users hear the active segment"), split it in the report: the attribute half is proven, the perception half is not, and the box stays unchecked because the item as written is not satisfied.

## Step 6: Honesty gate

> **Tick a box only for an item with a PASS and real evidence from the current head. Everything else stays unchecked.**

No "probably fine." No ticking a FAIL because the fix looks easy. No checking a subjective item because you hold an opinion. An honest "could not verify X" is far more useful to a reviewer than a false green check.

## Step 7: Reword, tick, record, push

Do it in one pass with the bundled helper. **Read `--help` before first use.**

Write `$WORK/evidence.md` covering every item (PASS, FAIL, and both BLOCKED kinds) so the reviewer sees the whole picture, not just the wins. Open it with the commit it describes, e.g. ``Verified on `246a9b9` ``.

Set `SKILL_DIR` to this skill directory, then run, for a generic test plan:

```bash
python3 "$SKILL_DIR/scripts/verify_checklist.py" \
  --body-file "$WORK/body.md" \
  --check "Importer retries three times on 503" \
  --section-file "$WORK/evidence.md" \
  --strict --out "$WORK/body_new.md"
```

For a dual-track body, pin placement and audit the table:

```bash
python3 "$SKILL_DIR/scripts/verify_checklist.py" \
  --body-file "$WORK/body.md" \
  --reword 'not yet observed at the time of writing::6/6 required checks pass on 246a9b9' \
  --check "CI on this PR" \
  --section-file "$WORK/evidence.md" \
  --before-heading "## Not included" \
  --audit-table --strict \
  --out "$WORK/body_new.md"
```

How the helper behaves:

- **`--check` ticks exactly one item**: the unchecked item whose full text equals the string, otherwise the only unchecked item containing it. A string found in several items ticks none of them; pass the full item text instead. With `--strict`, an ambiguous or unmatched string exits 2.
- **`--reword 'OLD::NEW'`** fixes an item that describes its own state ("not yet observed at the time of writing"), which would contradict itself once ticked. It follows the same one-item rule, never touches checked items, and runs before `--check`, so a check can target the new wording.
- **The evidence section** (`## QA Verification` unless `--section-title` says otherwise) is replaced, never stacked. It goes before `--before-heading` if given, else after the checklist under `--anchor-heading`, else after the first `##`..`######` heading naming test/checklist/QA/verification, else at the end. The H1 is never an anchor: it is the PR title.
- **`--audit-table`** warns when a ticked item's text also appears in a traceability row marked FAIL or MISSING. With `--strict`, that is exit 3.
- Re-running produces the same body. The checks then match only checked items, so `--strict` exits 2 on the re-run by design.

Diff, confirm the head has not moved, then push:

```bash
command diff -u "$WORK/body.md" "$WORK/body_new.md"
if [[ "$(command gh pr view <n> --json headRefOid --jq .headRefOid)" == "$HEAD_SHA" ]]; then
  command gh pr edit <n> --body-file "$WORK/body_new.md"
else
  echo "head moved since verification; nothing pushed" >&2
fi
```

If the head moved, your evidence describes an older commit. Redo the affected items on the new head before pushing anything.

### Reconcile the second record (dual-track bodies)

If a ticked item corresponds to a table row still reading MISSING, update the row too. If `## Not included / out of scope` lists something you just proved, remove that line. Leaving them stale re-creates the problem this skill exists to fix, one section lower.

## Step 8: Report

- **Verified on:** the short `HEAD_SHA`.
- **Ticked (N):** each item + one-line evidence.
- **Failed (N):** each item + what broke. Call these out; they may block merge.
- **Blocked, needs a human (N):** each item + who has to do it.
- **Blocked, deferred (N):** each item + which event unblocks it.
- Any table/out-of-scope lines you reconciled.
- The PR URL.

If nothing could be verified, say so plainly and do not edit the PR.

---

## Principles

- **Close the loop or it did not happen.** The deliverable is an updated PR body, not a verification you keep to yourself.
- **A checkmark is a claim.** Back every one with evidence of the right *kind*, from the commit that will merge.
- **A failed check is a gift.** Discovering that "persists across reload" is broken is the best possible outcome of running it.
- **Never manufacture the event.** Do not deploy, tag, or mutate production to close a box.
- **Touch only what you verified.** Preserve checked items, prose, and formatting exactly. Running twice equals running once.

## Examples

### Generic test plan

**Input:** PR #19, written by `pr-creator`:

```
## Test plan
- [x] Frontend unit/type suite green
- [ ] Visual QA of the tab strip on mobile widths (horizontal scroll behavior)
- [ ] Confirm category persistence across a full page reload in-browser
- [ ] PM sign-off on the Korean labels
```

The user adds: "I already ran QA and both browser items pass."

**Process:** Local `HEAD` equals `headRefOid` and the tree is clean. The user's report is a lead, so both browser items are re-run through webapp-testing against a dev server on the head: 320/375/414px widths (PASS) and switch tab, reload, assert active tab (PASS). PM sign-off is a human judgment (BLOCKED, needs a human).

**Output:** two boxes flipped with their full item text as `--check`, a `## QA Verification` section placed right after the test plan, the PM item left unchecked.

### Dual-track body

**Input:** a Delivery body with

```
## Verification
- [x] pytest -q → 631 passed
- [ ] **CI on this PR** — not yet observed at the time of writing
- [ ] **Screen-reader verification of aria-current** — the announcement needs a human
- [ ] **Tag-gate behavior on the new main** — unverifiable until a tag is pushed
```

**Process:** CI: `gh pr checks --required` all `pass`, and the check runs for `headRefOid` show the same names completed on `246a9b9` (PASS); the item is reworded so it no longer says "not yet observed". Screen reader: an e2e assertion proves the attribute, not the announcement (BLOCKED, needs a human). Tag gate: pushing a tag would deploy (BLOCKED, deferred).

**Report:**
> Ticked 1 of 3 on PR #96, verified on `246a9b9`. CI: PASS, 6/6 required checks pass on the head; the non-required `Deploy Production (Vercel)` correctly SKIPPED. Left unchecked: screen-reader announcement (needs a person with assistive tech; e2e proves the attribute, not the announcement) and tag-gate behavior (deferred; proving it means pushing a tag, which deploys).
