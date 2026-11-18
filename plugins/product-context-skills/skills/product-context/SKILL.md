---
name: product-context
description: Use when installing or diagnosing product-context, preparing a PR for a product with wiki automation, checking whether subscription wiki setup is complete, or when specifications, decisions, implementation evidence, or handoff documents may be stale.
license: MIT
---

# Product Context

Reference for the **offline CLI** and optional **subscription-host wiki MCP**. A changed decision is legitimate;
retain its reason, scope, predecessors, and unresolved questions. Evidence
freshness is separate from semantic correctness and product acceptance.

## Connect a product and verify completion

For installation, PR automation, or missing OAuth/API messages, read
[product setup](references/product-setup.md). Resolve its scripts relative to this
skill. The product-aware entry point is:

```sh
python3 scripts/product_setup.py doctor --repo /product --github-repo OWNER/REPO --host both --json
```

Its required completion report has three separate rows: **local installation**
(`local`), **this product's PR configuration** (`automation`), and **actual PR
publication** (`verification`). Include their status, missing/unknown check codes,
and next actions. `complete` requires all three; secret presence alone leaves
authentication unverified until a real writer succeeds. `unknown` means inspection
was unavailable. It does not mean the credential is absent.

When the user chooses PR automation, use the integrated `setup` path with their
reviewed source profile and runtime pin. Complete the OAuth registration stage or
report the exact incomplete step. Preserve existing secrets. A local login does
not supply a GitHub runner credential. Use subscription OAuth, not an API key.

For a product with `.product-context/automation.json` or the configured wiki
workflow, run doctor before creating its PR and again with `--pr NUMBER` after its
run. Use the existing product opt-in across sessions. The final report names the
matching run URL, source snapshot and published commit; skipped generation or a
successful harness test is not proof for another product.

## Run the tool

Resolve `scripts/product_context.py` relative to this SKILL.md, then invoke it
through `python3` (Python 3.10+). Use the explicit product root with `--repo`;
the installed skill directory is not the product. All commands have `--help`.

| Operation | Command suffix |
|---|---|
| Connect a product locally | `init --repo /product --product product-name` |
| Inspect without writes | `check --repo /product --json` |
| Prepare a selective-reading packet | `prepare --repo /product` |
| Record an inspected snapshot | `record --repo /product --snapshot HASH --actor agent:codex --note "What was reviewed"` |
| Append a decision | `decision --repo /product --file /tmp/decision.json` |

The installed canonical invocation is:

```sh
python3 /path/to/product-context/scripts/product_context.py check --repo /path/to/product --json
```

Without local setup, `check` and `prepare` accept `--config /path/to/profile.json`.
The bundled `assets/houmdesk.json` is an example profile, not a universal policy.
Product files stay in that product: `.product-context.json` and
`.product-context/{review,decisions}.json`. Commit them there if review state
should travel between checkouts. Preserve existing document conventions.

## Read the result

- `unreviewed`/`stale`: inspect changed paths and relevant review topics. Do not
  infer a contradiction from a changed hash. Semantic contradictions need review.
- `current`: the recorded evidence versions match; this is not release approval,
  proof of implementation correctness, or closure of listed questions.
- Decisions retain their original records. A proposed replacement leaves the
  accepted choice in force. An accepted replacement links `supersedes`; a
  reconsideration links `reconsiders` and keeps the earlier choice visible.
- Record only the exact inspected snapshot. Changed evidence requires another
  inspection. `--question` preserves an open question; resolve it explicitly with
  `--resolve-question` after obtaining the answer.

Exit codes: `0` inspection completed (including expected drift), `1` missing
local references or explicitly required freshness, `2` invalid/unsafe input or
state. `--require-reviewed` is an opt-in freshness policy. These are the offline
CLI's exit codes; product setup has its own documented readiness exit codes.

## Subscription wiki maintenance

For manual wiki updates, read [subscription workflow](references/subscription-wiki.md).
For PR-driven updates, read [PR automation](references/pr-automation.md). A repository
workflow enabled by the user authorizes its bounded update on each eligible PR event;
the user does not need to request another update in each development session.
The current Claude Code/Codex session researches and writes; the `product_context`
MCP manages OpenWiki's queue and evidence without starting another model.

Complete source/spec/decision edits **before** `openwiki_begin`. Existing wikis
update; interrupted runs resume. Use the assigned page queue and its budget.
Finish must pass without `SOURCE_CHANGED`; then inspect `product_context_status`
and call `product_context_record_review` with the exact snapshot and explicit
questions from documents plus existing open questions. Never bypass a failed wiki
finish with the raw CLI `record`. Missing rationale remains unknown or explicitly
inferred; do not invent an approval or close an unanswered question.

## Cost boundary

Offline commands start no LLM, OpenWiki, network request, background job or
validation command. `prepare` prints references only. The optional MCP checks the
host's subscription login, starts no model/provider, suppresses OpenWiki's default
API workflow, and installs no schedule. Reading and writing still consume the
current host session's allowance; login checks are not billing receipts. Generation
requires an explicit request or a user-enabled repository PR workflow. The PR writer
uses Claude subscription OAuth regardless of which coding agent authored the PR.
Never treat a packet as proof that generation ran.

See [record formats and decisions](references/format.md). Existing product
guidance and user decisions take precedence over this reference.
