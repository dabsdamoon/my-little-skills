# Claude (Anthropic API) Cost Guide

Model IDs, prices, and cache minimums: [../provider-facts.md](../provider-facts.md). In the examples, `MODEL` stands for an ID from that table.

For deeper Claude-only work, the bundled `claude-api` skill has the authoritative references: `shared/prompt-caching.md` (placement patterns, silent invalidators, invalidation hierarchy) and `shared/cost-optimization.md`, which `/claude-api cost-optimize` runs as a full cost pass over existing Claude code.

## Prompt caching

Caching is a prefix match over the rendered request, in the order `tools` -> `system` -> `messages`. A one-byte change at position N invalidates every cache entry at or after N.

### Explicit breakpoints

Put `cache_control` on the last block of each stable section. Up to 4 breakpoints per request.

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model=MODEL,
    max_tokens=16000,
    system=[
        {
            "type": "text",
            "text": STABLE_INSTRUCTIONS_AND_REFERENCE,
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": per_request_input}],
)
```

A breakpoint on the last system block caches tools and system together. For a shared preamble followed by a varying question in the same user turn, put the marker on the shared block, not the last block, or every request writes a new entry that is never read.

### Automatic caching

A top-level `cache_control` field on the request places one breakpoint on the last cacheable block and moves it forward as a conversation grows. It is the simplest choice for multi-turn chat. It is the wrong choice when the prompt ends in unique per-request content: every request then pays the write premium on bytes nobody reads. It uses one of the 4 breakpoint slots and is rejected (400) on the legacy Amazon Bedrock integration for Opus 4.6 and earlier.

The robust shape for agent loops: one explicit breakpoint on the static system prefix, plus top-level automatic caching for the growing tail.

### TTL

```python
{"type": "ephemeral"}               # 5-minute TTL (default), write 1.25x
{"type": "ephemeral", "ttl": "1h"}  # 1-hour TTL, write 2x
```

A cache read refreshes the timer at no extra cost, and the lifetime counts from the start of the request. Choose by the start-to-start gap between requests that share the prefix:

| Gap | TTL |
|---|---|
| Under 5 minutes | 5-minute (every request refreshes it) |
| 5 to 60 minutes | 1-hour |
| Over an hour | Neither; re-warm on a schedule or accept the miss |

Break-even: with the 5-minute TTL, two requests (1.25x + 0.1x against 2x uncached); with the 1-hour TTL, three. On models with cheaper reads (see the facts file) the break-even comes sooner.

### What silently breaks the cache

- Timestamps, request IDs, or user names interpolated into `system`
- `json.dumps` without `sort_keys=True`, or tool lists built per user
- Adding, removing, or reordering tools, or switching models mid-conversation
- Changing `thinking` or top-level `output_config.effort` between requests
- Changing `output_config.format` (the structured-output schema)
- A prefix below the model's minimum: no error, just `cache_creation_input_tokens: 0`

Move dynamic content after the last breakpoint, or into a later message.

### Verify from usage, not from code review

```python
u = response.usage
print(u.cache_creation_input_tokens, u.cache_read_input_tokens, u.input_tokens)
```

`input_tokens` is only the uncached remainder; total prompt size is the sum of the three. On the second identical request, `cache_read_input_tokens` must be non-zero. Re-check after every change to prompt assembly - regressions are silent and only show on the bill.

## Thinking and effort

Thinking tokens bill as output and count toward `max_tokens`. On current models, use adaptive thinking and steer cost with effort; `budget_tokens` returns a 400 on newer models (see the facts file).

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "medium"},
    messages=[{"role": "user", "content": task}],
)
```

Lower effort first when thinking dominates the bill; it scales thinking, tool calls, and text together. Sweep effort on your own eval - quality cost varies by workload. Keep effort constant within a cached conversation (or use per-message effort where the model supports it) because a top-level change invalidates the messages cache.

## Structured outputs

Use `output_config.format` instead of "return JSON only" instructions, prefill, or retry-on-parse loops:

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Extract the contact details:\n{text}"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["name", "email"],
                "additionalProperties": False,
            },
        }
    },
)
```

Structured outputs add a small injected system prompt (billed as input). Keep the schema stable: changing it invalidates the prompt cache and the compiled-grammar cache.

## Sampling parameters

Do not send `temperature`, `top_p`, or `top_k` to control cost or output format. They are removed in API version `2026-10-21` and rejected with non-default values on Claude 4.7 and later under earlier versions.

## Other levers

- **Batch API**: 50% off every token, cache reads and writes included, for work nobody waits on (results within 24 hours).
- **Token counting**: `client.messages.count_tokens(model=MODEL, system=..., messages=[...])` returns `.input_tokens`. It is free (rate-limited) and counts with the tokenizer of the model you pass. Do not use `tiktoken` for Claude.
- **Large reference documents**: cache them when most requests read most of them; move them behind a tool or retrieval when requests need only a section.
- **Many tool schemas**: cache the tool block (tools render first) and keep the list stable; past roughly 10K schema tokens consider tool search with `defer_loading`.
