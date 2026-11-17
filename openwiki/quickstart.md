---
type: guide
title: Quickstart
description: What my-little-skills provides and how the product-context wiki workflow operates
tags: [product, skills, product-context]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-17T01:35:30.771Z
sources:
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-f281d8132c7b47b7d987a87c
    resource: repo://skills/product-context/references/subscription-wiki.md
  - id: openwiki-source-901fc0d98522e338a3c22bbb
    resource: repo://skills/product-context/SKILL.md
generated: { by: "claude-code", at: "2026-11-17T01:35:30.771Z" }
---

# Quickstart

## What this repository is

my-little-skills is a curated Agent Skills and plugin marketplace for Codex/OpenAI, Claude Code, Claude and Cowork. It bundles Anthropic's upstream skills with custom skills for developer workflow, analysis, security, writing, design and other domains.

## Install

- Claude Code: `/plugin marketplace add dabsdamoon/my-little-skills`, then `/plugin install <plugin-name>@my-little-skills`.
- Codex: `codex plugin marketplace add dabsdamoon/my-little-skills --ref main`, then `codex plugin add <plugin>@my-little-skills`.
- `pr-creator` is distributed only through `developer-workflow-skills`; `humanize-korean` requires explicitly installing `writing-skills`.

## Product-context harness

The `product-context` skill provides an offline CLI that checks product evidence (specs, decisions, open questions) for staleness, plus an optional local MCP bridge for subscription-host OpenWiki maintenance.

- Offline commands (`init`, `check`, `prepare`, `record`, `decision`) start no model, network request or background job.
- A `current` result means recorded evidence versions match. It is not release approval or proof of correctness.
- Wiki updates use the current subscription-authenticated host session. There is no API-key fallback or scheduled API generation.
- Lifecycle: `openwiki_begin`, `openwiki_submit_plan`, `openwiki_next_page`, `openwiki_submit_page`, `openwiki_finish`, then `product_context_status` and `product_context_record_review`.
- The default work budget is three pages including quickstart.
- An opt-in PR workflow can maintain the wiki using Claude subscription OAuth.

## Open questions

No open questions are recorded in the source documents reviewed. Review state was unreviewed before this run.
