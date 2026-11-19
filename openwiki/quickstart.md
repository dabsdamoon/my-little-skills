---
type: guide
title: Quickstart
description: What my-little-skills provides and how the product-context wiki workflow operates
tags: [product, skills, product-context]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-19T00:56:22.195Z
sources:
  - id: openwiki-source-e806ba82c1dc93b631154825
    resource: repo://plugins/product-context-skills/README.md
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-f281d8132c7b47b7d987a87c
    resource: repo://skills/product-context/references/subscription-wiki.md
  - id: openwiki-source-901fc0d98522e338a3c22bbb
    resource: repo://skills/product-context/SKILL.md
generated: { by: "claude-code", at: "2026-11-19T00:56:22.195Z" }
---

# Quickstart

## What this repository is

my-little-skills is a curated Agent Skills and plugin marketplace for Codex/OpenAI, Claude Code, Claude and Cowork. It bundles Anthropic's upstream skills with custom skills for developer workflow, analysis, security, writing, design and other domains.

## Install

- Claude Code: `/plugin marketplace add dabsdamoon/my-little-skills`, then `/plugin install <plugin-name>@my-little-skills`.
- Codex: `codex plugin marketplace add dabsdamoon/my-little-skills --ref main`, then `codex plugin add <plugin>@my-little-skills`.
- `pr-creator` is distributed only through `developer-workflow-skills`; `humanize-korean` requires explicitly installing `writing-skills`.

## Visual explainer and licensing

- `visual-explainer` is bundled in `design-skills` for Claude Code and Codex. It turns concepts, flows, plans and changes into HTML figures; invoke `/design-skills:visual-explainer` in Claude Code or `$visual-explainer` in Codex. Its upstream record pins v0.15.0 and keeps the original MIT notices. Basic rendering needs Node.js.
- Maintainer-authored skills listed in `LICENSING.md` are MIT licensed with standalone license files. Imported skills and assets keep their own licenses and attribution.

## Model comparisons

- `research-workflow-skills` includes `model-quality-compare`. The default GPT pilot uses four CLI calls with 24 original text cases and objective grading, records category scores, repeatability, token usage and wall time, and produces an HTML report. It never silently switches to API billing.
- Its artifact workflow compares implementation, structure and research outcomes using independent writable starter copies, actual code and data outputs, frozen executable checks and separate blinded review. The expanded low-effort evaluation preserves both models' code, reports, dataset notices and numerical checks.
- Native-host controls also support exact Claude model IDs through Claude.ai subscription login. A fresh-session Terra/Sonnet comparison records context exclusions, eight distinct sessions, unchanged task hashes, and separate objective versus interpretive results.
- The GPT 6.1/6.2 pilot reached 100% for both models, so it cannot establish a general winner.

## Product-context harness

The `product-context` skill provides an offline CLI that checks product evidence (specs, decisions, open questions) for staleness, plus an optional local MCP bridge for subscription-host OpenWiki maintenance.

- Offline commands (`init`, `check`, `prepare`, `record`, `decision`) start no model, network request or background job.
- A `current` result means recorded evidence versions match. It is not release approval or proof of correctness.
- Wiki updates use the current subscription-authenticated host session. There is no API-key fallback or scheduled API generation.
- Lifecycle: `openwiki_begin`, `openwiki_submit_plan`, `openwiki_next_page`, `openwiki_submit_page`, `openwiki_finish`, then `product_context_status` and `product_context_record_review`.
- The default work budget is three pages including quickstart.
- An opt-in PR workflow can maintain the wiki using Claude subscription OAuth.

## Plugin and setup details

- The `product-context-skills` plugin README says it is installable from the my-little-skills marketplace: `/plugin install product-context-skills@my-little-skills` (Claude Code) or `codex plugin add product-context-skills@my-little-skills` (Codex).
- The root `skills/product-context` is the canonical bundle; the plugin's copy is its exact distribution mirror.
- MCP setup is an explicit per-machine step (`setup_subscription_wiki.py --host both`, read-only plan first, then `--install`). It needs Python 3.10+, Node.js 22.22+, npm and subscription logins, and installs a pinned OpenWiki 0.9.0 runtime with npm scripts disabled under `~/.local/share/product-context/<runtime-version>`, where the version comes from `skills/product-context/runtime/package.json`.
- Existing custom workflows are preserved and block generation.

## Product-aware setup and completion report

- `product_setup.py` (`doctor`, `setup`, `oauth`) is the product-aware entry point for PR automation. Its completion report has three separate rows: local installation, this product's PR configuration, and actual PR publication. `complete` requires all three; `unknown` means inspection was unavailable, not that a credential is absent.
- Setup stays incomplete until product configuration and Actions subscription OAuth are provided. A token is issued interactively with `claude setup-token` and supplied through the hidden-input `oauth` command, never pasted into chat. Existing secrets are preserved.
- For a product with the PR workflow, run `doctor` before creating the PR and again with `--pr NUMBER` afterwards. Generating the workflow alone does not activate cloud generation.

## Open questions

No open questions are recorded in the source documents reviewed.
