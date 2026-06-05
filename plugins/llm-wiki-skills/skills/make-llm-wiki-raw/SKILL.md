---
name: make-llm-wiki-raw
description: Create raw source notes for the user's Obsidian LLM-Wiki vault from pasted text, URLs, local files, PDFs, docs, screenshots, meeting notes, or repository artifacts. Use when the user asks to capture, add, save, stage, or make something raw for LLM-Wiki before wikification.
---

# Make LLM Wiki Raw

Create source-of-truth material in the LLM-Wiki raw layer. Do not wikify, summarize into entities, or update `wiki/` unless the user also invokes `wikify-raw`.

## Vault

Resolve the target vault in this order:

1. A vault path explicitly provided by the user.
2. The current working directory, if it contains `AGENTS.md`, `raw/`, and `wiki/`.
3. The `LLM_WIKI_VAULT` environment variable, if available.
4. The personal default `/Users/dabsdamoon/LLM-Wiki/LLM-Wiki`, if it exists.

If none resolve, stop before writing and ask the user: "What is the path to your LLM-Wiki vault?" Do not guess or create a new vault implicitly.

If the user gives another vault path, use that path. Before writing, verify the vault has `AGENTS.md`, `raw/inbox/`, and `wiki/`. If `raw/inbox/` is missing but the vault is clearly an LLM-Wiki vault, create the missing raw directories only.

## Workflow

1. Identify the input type: pasted text, URL, local file, binary attachment, repository artifact, or mixed sources.
2. Read `AGENTS.md` if present and obey its raw-layer contract.
3. Read the bundled Web Clipper template at `assets/llm-wiki-raw-source-clipper.json` relative to this skill, and use its `noteContentFormat`, `noteNameFormat`, and `path` as the canonical raw note format.
4. Create exactly one raw inbox note per source unless the user asks for a batch.
5. Preserve the source content as directly as practical. Do not rewrite it into a wiki summary.
6. Put markdown/text sources under the template path, normally `raw/inbox`.
7. Put binary assets under `raw/assets/` and create a raw wrapper note that follows the same frontmatter shape where practical.
8. Never overwrite an existing raw note. If a filename collides, append a short suffix.
9. Do not update `wiki/index.md`, `wiki/log.md`, or generated pages.

## Raw Note Format

For web, pasted text, and markdown/text captures, mirror `assets/llm-wiki-raw-source-clipper.json`. The current canonical template is:

```markdown
---
type: raw_source
source_type: web
title: "Title"
url: ""
site: ""
author: ""
published: ""
clipped: "YYYY-MM-DDTHH:MM:SS+TZ"
status: inbox
---

# Title

Source: URL

Original content goes here.
```

For non-web text sources, keep the same shape for consistency. Set `source_type` to `file`, `meeting`, `repo`, `manual`, or `other`; set `url` to `""`; put the local path or origin in the `Source:` line; and use `clipped` for the capture timestamp.

For binary files, copy or reference the asset and create a wrapper note:

```markdown
---
type: raw_source
source_type: pdf|doc|image|other
title: "Title"
url: ""
site: ""
author: ""
published: ""
clipped: "YYYY-MM-DDTHH:MM:SS+TZ"
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
