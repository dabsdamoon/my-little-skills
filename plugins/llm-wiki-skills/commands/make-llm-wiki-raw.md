Use the `make-llm-wiki-raw` skill.

Input:

```text
$ARGUMENTS
```

Create raw source note(s) in the LLM-Wiki vault. Use the vault path provided by the user, the current working directory if it is an LLM-Wiki vault, `LLM_WIKI_VAULT` if set, or the personal default `/Users/dabsdamoon/LLM-Wiki/LLM-Wiki` if it exists. Read `AGENTS.md` when present. Write to `raw/inbox/` and `raw/assets/` only. Do not update `wiki/`, `wiki/index.md`, or `wiki/log.md`.

Use the bundled template at `skills/make-llm-wiki-raw/assets/llm-wiki-raw-source-clipper.json` as the canonical raw note template. Mirror its `noteContentFormat`, `noteNameFormat`, and `path` so skill-created raw notes match Obsidian Web Clipper output.

End with the created raw path(s) and the next `wikify-raw` command to run.
