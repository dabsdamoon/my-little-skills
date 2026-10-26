# OpenAI Cost Guide

Model IDs, prices, cache minimums, and deprecations: [../provider-facts.md](../provider-facts.md). In the examples, `MODEL` stands for an ID from that table. Examples use the Responses API, which OpenAI recommends for new projects; Chat Completions remains supported.

## Prompt caching

Caching is enabled by default on supported models and matches on the request prefix. Stable content first, dynamic content last:

- Put stable instructions and shared reference material first.
- Put timestamps, user-specific content, and other dynamic material at the end.
- Append new turns; do not rewrite earlier ones.
- Keep tool definitions, their order, and schemas identical across requests. To vary which tools the model may call without changing the list, use `allowed_tools` in `tool_choice`.

### GPT-5.6 and later: implicit and explicit breakpoints

By default OpenAI places one implicit breakpoint at the end of the latest eligible message. To control placement, add explicit breakpoints on content blocks; set `prompt_cache_options.mode` to `explicit` to disable the implicit one. A request can create up to four cache writes. Cache writes are billed at a premium over uncached input (see the facts file), so a breakpoint after content that never repeats is a pure surcharge.

Request body shape (Responses API):

```json
{
  "model": "MODEL",
  "prompt_cache_options": {"mode": "explicit"},
  "input": [
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "Stable instructions and reference material...",
          "prompt_cache_breakpoint": {"mode": "explicit"}
        }
      ]
    },
    {"role": "user", "content": "The per-request question..."}
  ]
}
```

`prompt_cache_options.ttl` sets the lifetime (`30m` default; the guide also documents `12h` for the Responses API). Without explicit breakpoints in explicit mode, the request does not use caching at all.

### Earlier models

Caching is automatic with no breakpoints. Send a stable `prompt_cache_key` on related requests to improve routing to the same cache (it influences routing; it does not guarantee a hit). `prompt_cache_retention` (`in_memory` or `24h`) sets retention; the current SDK marks it deprecated in favor of `prompt_cache_options.ttl`.

### Verify from usage

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model=MODEL,
    instructions=STABLE_INSTRUCTIONS,
    input=per_request_input,
)
details = response.usage.input_tokens_details
print(details.cached_tokens, details.cache_write_tokens)
```

On the second identical request, `cached_tokens` must be non-zero. If it stays at zero, diff the two request bodies for anything that changed in the prefix. Note that `previous_response_id` does not carry the previous response's `instructions` forward - resend them unchanged on each request.

## Structured outputs

In the Responses API, `text.format` replaces Chat Completions' `response_format`:

```python
response = client.responses.create(
    model=MODEL,
    instructions="Extract the contact details.",
    input=text,
    text={
        "format": {
            "type": "json_schema",
            "name": "contact",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": ["string", "null"]},
                },
                "required": ["name", "email", "phone"],
                "additionalProperties": False,
            },
        }
    },
)
```

A schema with only the fields the caller reads is the output-token lever; the strict schema replaces "return valid JSON" instructions and retry-on-parse code.

## Reasoning and output length

- `max_output_tokens` is an upper bound on visible output **plus reasoning tokens**. Set it as a backstop with headroom; a tight cap truncates reasoning and wastes the attempt.
- To spend less on reasoning, lower `reasoning={"effort": ...}` and measure quality on your eval. Supported levels vary by model (see the models page).
- To shorten visible output, specify the output shape, ideally with an example.

## Tool definitions

Function definitions are billed as input tokens on every request. OpenAI's guidance is to write clear and detailed names, parameter descriptions, and instructions - do not cut descriptions to one-liners to save tokens, because under-described tools are the more expensive failure. Reduce tool tokens instead by:

- Loading fewer functions up front (OpenAI suggests fewer than 20 at the start of a turn as a soft guideline)
- Tool search, so deferred tools load only when needed
- Keeping the tool list stable so it stays in the cached prefix

## Other levers

- **Batch API**: roughly half price for work nobody waits on.
- **Token counting**: `client.responses.input_tokens.count(model=MODEL, input=..., instructions=...)` returns `.input_tokens` without running the model.
