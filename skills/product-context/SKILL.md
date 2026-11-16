---
name: product-context
description: Use when product specifications, ADRs, implementation evidence, or handoff documents may be stale, when decisions change or need reconsideration, or when an offline product-context check is needed across repositories.
---

# Product Context

Reference for the bundled **offline** CLI. A changed decision is legitimate;
retain its reason, scope, predecessors, and unresolved questions. Evidence
freshness is separate from semantic correctness and product acceptance.

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
state. `--require-reviewed` is an opt-in freshness policy.

## Cost boundary

The CLI starts no LLM, OpenWiki, network request, background job, or configured
validation command. `prepare` prints instructions and references only. Skill
selection and reading still consume the current agent session's allowance.
Automatic checks do not authorize model-based generation. When the user
explicitly requests generation, the current agent can use the packet for a
scoped document update; optional OpenWiki usage follows that separately chosen
execution/billing mode. Never treat a prepared packet as evidence that generation
ran. No provider execution adapter is shipped in this version.

See [record formats and decisions](references/format.md). Existing product
guidance and user decisions take precedence over this reference.
