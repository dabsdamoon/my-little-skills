Use the `make-llm-wiki-raw` skill.

Input:

```text
$ARGUMENTS
```

Create raw source note(s) in the LLM-Wiki vault. Use `/Users/dabsdamoon/LLM-Wiki/LLM-Wiki` unless the user provides another vault path. Read `AGENTS.md` when present. Write to `raw/inbox/` and `raw/assets/` only. Do not update `wiki/`, `wiki/index.md`, or `wiki/log.md`.

End with the created raw path(s) and the next `wikify-raw` command to run.
