---
name: wikify-raw
description: Ingest raw sources from the user's Obsidian LLM-Wiki vault into generated wiki pages. Use when the user asks to wikify, ingest, process, connect, or convert raw/inbox or raw/sources documents into source summaries, entities, concepts, syntheses, index updates, and log entries.
---

# Wikify Raw

Turn raw LLM-Wiki material into a connected Obsidian wiki. Treat `raw/` as source-of-truth and `wiki/` as the generated knowledge layer.

## Vault

Default vault:

```text
/Users/dabsdamoon/LLM-Wiki/LLM-Wiki
```

If the user gives another vault path, use it. Always read `AGENTS.md` first when it exists.

## Input Selection

- If the user names files, process only those files.
- If the user says "all", "inbox", or gives no file, inspect `raw/inbox/` and process raw notes not already represented in `wiki/sources/` or `wiki/log.md`.
- Never modify, move, rename, or delete raw files unless the user explicitly asks.

## Required Reads

Before generating pages:

1. Read `AGENTS.md`.
2. Read `wiki/index.md` if present.
3. Read the selected raw source.
4. Search existing `wiki/entities/`, `wiki/concepts/`, and `wiki/syntheses/` for likely matches before creating new pages.

## Ingest Workflow

For each selected raw source:

1. Create or update one source summary in `wiki/sources/`.
2. Extract key claims, dates, entities, concepts, contradictions, and open questions.
3. Create entity pages only for durable things likely to matter again: people, organizations, products, projects, papers, places, events, datasets, books, or recurring objects.
4. Create concept pages only for reusable ideas, methods, frameworks, and terms.
5. Update existing pages before creating duplicates. Add aliases when sources use alternate names.
6. Add Obsidian wikilinks between source, entity, concept, synthesis, and question pages.
7. Create or update synthesis pages only when the source changes a bigger picture or connects multiple pages.
8. Update `wiki/index.md` as a routing index only.
9. Append a dated entry to `wiki/log.md`.

## Page Templates

Source summaries should use:

```markdown
---
type: source
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft
sources:
  - raw/path/to/source.md
aliases: []
tags: []
---

# Source - Title

## Summary

## Key Claims

## Entities

## Concepts

## Dates and Timeline

## Contradictions or Tensions

## Open Questions
```

Entity pages should use:

```markdown
---
type: entity
entity_type: person|organization|product|project|paper|event|place|dataset|book|other
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft
sources: []
aliases: []
related: []
tags: []
---

# Entity Name

## Summary

## Key Facts

## Relationships

## Timeline

## Contradictions

## Open Questions
```

## Index Guardrails

`wiki/index.md` is a router, not a knowledge dump.

Keep each entry to:

```text
[[Page]] - one-line description and why it matters.
```

Do not put long summaries, timelines, detailed claims, or evidence tables in the index. If `index.md` grows beyond roughly 250 lines, create or update sub-indexes under `wiki/_indexes/` and keep the top-level index short.

## Size Guardrails

Use these rough caps:

```text
source summary: 500-1500 words
entity/concept page: 500-1200 words
synthesis page: 1000-2500 words
frontmatter arrays: 10-20 important links
query read budget: index plus 3-8 relevant pages first
```

If a page gets too large:

1. Split stable subtopics into child pages.
2. Replace long sections with short summaries and links.
3. Preserve citations and backlinks.
4. Log the restructuring.

## Citation Rules

- Cite the generated source page for wiki claims, and make that source page point back to the raw file.
- Use Obsidian wikilinks for durable relationships.
- Mark uncertain claims as uncertain.
- If sources disagree, add or update a `Contradictions` section.

## Completion

End with a concise report:

- Raw files processed.
- Source/entity/concept/synthesis pages created or updated.
- Whether `wiki/index.md` and `wiki/log.md` were updated.
- Any unresolved issues, large-source limits, or citations that need human review.
