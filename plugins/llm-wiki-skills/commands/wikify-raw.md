Use the `wikify-raw` skill.

Input:

```text
$ARGUMENTS
```

Ingest selected raw source(s) from the LLM-Wiki vault. Use the vault path provided by the user, the current working directory if it is an LLM-Wiki vault, `LLM_WIKI_VAULT` if set, or the personal default `/Users/dabsdamoon/LLM-Wiki/LLM-Wiki` if it exists. If none resolve, ask the user for the vault path before writing. Read `AGENTS.md` first. Do not modify `raw/`. Create or update generated pages under `wiki/`, keep `wiki/index.md` as a routing index, and append to `wiki/log.md`.

End with a concise report of raw files processed and wiki pages created or updated.
