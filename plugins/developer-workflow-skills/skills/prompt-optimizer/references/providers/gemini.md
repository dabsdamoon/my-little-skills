# Google Gemini Cost Guide

Model IDs, prices, cache minimums, and storage rates: [../provider-facts.md](../provider-facts.md). In the examples, `MODEL` stands for an ID from that table. Examples use the `google-genai` SDK (`from google import genai`); the older `google-generativeai` package is deprecated.

## Implicit caching

Implicit caching is on by default for Gemini 2.5 and newer models; cost savings are passed on automatically when a request hits the cache. It is a prefix match, so the same structure rules apply as everywhere else: stable system instruction, tools, and shared documents first; the per-request question last. Each model has a minimum input size below which nothing caches (see the facts file).

For the newest models (`gemini-4-argon` and later), implicit caching is the only option - structure the prompt for it.

## Explicit caching

On models that support it, create a cache object once and reference it from each request. Storage is billed for the TTL, so explicit caching pays only when enough requests read the cache within that window.

```python
from google import genai
from google.genai import types

client = genai.Client()

cache = client.caches.create(
    model=MODEL,
    config=types.CreateCachedContentConfig(
        system_instruction=STABLE_INSTRUCTIONS,
        contents=[large_document],
        ttl="3600s",
    ),
)

response = client.models.generate_content(
    model=MODEL,
    contents="Summarize the key points.",
    config=types.GenerateContentConfig(cached_content=cache.name),
)
```

- TTL defaults to 1 hour; set `ttl` (a duration string such as `"3600s"`) or `expire_time`. Delete caches you no longer need with `client.caches.delete(name=cache.name)` so storage stops billing.
- Break-even: compare (requests per TTL window x input tokens saved x (input price - cached price)) against (cached tokens x storage price x hours).

## Verify from usage

```python
print(response.usage_metadata.cached_content_token_count)
```

A zero or missing value on a request you expected to hit means the prefix changed or is below the model's minimum.

## Structured output

```python
response = client.models.generate_content(
    model=MODEL,
    contents=f"Extract the contact details:\n{text}",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["name", "email"],
        },
    ),
)
```

Request only the fields the caller reads.

## Thinking and output length

Gemini bills thinking tokens at the output rate. Where the model supports it, lower thinking through `thinking_config` (`thinking_level` or `thinking_budget`, depending on the model) and measure quality on your eval. To shorten visible output, specify the output shape, ideally with an example.

## Other levers

- **Batch**: 50% off for work nobody waits on.
- **Token counting**: `client.models.count_tokens(model=MODEL, contents=...)` returns `.total_tokens`.
- **Long context**: a large context window makes it tempting to inline everything on every call. Cache material that most requests read; retrieve material that only some requests need.
