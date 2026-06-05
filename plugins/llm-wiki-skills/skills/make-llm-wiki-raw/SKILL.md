---
name: make-llm-wiki-raw
description: Create raw source notes for the user's Obsidian LLM-Wiki vault from pasted text, URLs, local files, PDFs, docs, screenshots, meeting notes, or repository artifacts. Use when the user asks to capture, add, save, stage, or make something raw for LLM-Wiki before wikification.
---

# Make LLM Wiki Raw

Create source-of-truth material in the LLM-Wiki raw layer. Do not wikify, summarize into entities, or update `wiki/` unless the user also invokes `wikify-raw`.

## Vault

Default vault:

```text
/Users/dabsdamoon/LLM-Wiki/LLM-Wiki
```

If the user gives another vault path, use that path. Before writing, verify the vault has `AGENTS.md`, `raw/inbox/`, and `wiki/`. If `raw/inbox/` is missing but the vault is clearly an LLM-Wiki vault, create the missing raw directories only.

## Workflow

1. Identify the input type: pasted text, URL, local file, binary attachment, repository artifact, or mixed sources.
2. Read `AGENTS.md` if present and obey its raw-layer contract.
3. Create exactly one raw inbox note per source unless the user asks for a batch.
4. Preserve the source content as directly as practical. Do not rewrite it into a wiki summary.
5. Put markdown/text sources under `raw/inbox/`.
6. Put binary assets under `raw/assets/` and create a `raw/inbox/` note that links to the asset.
7. Never overwrite an existing raw note. If a filename collides, append a short suffix.
8. Do not update `wiki/index.md`, `wiki/log.md`, or generated pages.

## Raw Note Format

Use this format for a captured markdown source:

```markdown
---
type: raw_source
source_type: web|file|pdf|doc|screenshot|meeting|repo|manual|other
title: "Title"
url: ""
source_path: ""
captured: YYYY-MM-DD
status: inbox
---

# Title

Source: URL or local path

Original content goes here.
```

For binary files, copy or reference the asset and create a wrapper note:

```markdown
---
type: raw_source
source_type: pdf|doc|image|other
title: "Title"
source_path: "raw/assets/file.ext"
captured: YYYY-MM-DD
status: inbox
---

# Title

Source asset: [[raw/assets/file.ext]]

## Notes

This raw source points to the attached asset. Extracted text may be added here only if available without losing the original asset.
```

## URL Handling

If the user gives a URL:

- Prefer the user's clipped Obsidian Web Clipper output if it already exists.
- If network access is available and appropriate, fetch readable page content and save it as a raw inbox note.
- If network access is blocked or approval is needed, create a pending raw note containing the URL and status `pending_fetch`, then tell the user to clip it with Obsidian Web Clipper or approve fetching.

## Naming

Use readable filenames:

```text
raw/inbox/YYYY-MM-DD - Short Title.md
```

Keep names filesystem-safe. Preserve the original title in frontmatter even if the filename is shortened.

## Completion

End with:

- The raw note path created.
- Any asset path created.
- The exact next command the user can run, for example:

```text
Use $wikify-raw raw/inbox/YYYY-MM-DD - Short Title.md
```
