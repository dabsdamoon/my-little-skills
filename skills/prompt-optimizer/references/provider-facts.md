# Provider Facts (checked 2026-10-26)

Every model ID, price, cache minimum, and retirement date this skill uses lives in this file and nowhere else. Prices change often: re-open the source page before quoting a number to the user, and when the page and this table disagree, the page wins. Prices are USD per million tokens (MTok).

## Anthropic (Claude API)

Sources: `https://platform.claude.com/docs/en/about-claude/pricing`, `.../about-claude/models/overview`, `.../build-with-claude/prompt-caching`, `.../about-claude/model-deprecations`, `.../api/versioning`.

| Model ID | Input | 5m cache write | 1h cache write | Cache read | Output | Cache minimum |
|---|---|---|---|---|---|---|
| `claude-fable-5-1` | $10 | $12.50 | $20 | $0.25 | $50 | 512 |
| `claude-opus-5-5` | $4 | $5 | $8 | $0.20 | $20 | 512 |
| `claude-sonnet-5-5` | $2 | $2.50 | $4 | $0.10 | $10 | 512 |
| `claude-haiku-5-5` (prompt up to 100K tokens) | $0.10 | $0.125 | $0.20 | $0.01 | $0.50 | 512 |
| `claude-haiku-5-5` (prompt over 100K tokens) | $0.50 | $0.625 | $1 | $0.05 | $2.50 | 512 |
| `claude-opus-5` (legacy) | $5 | $6.25 | $10 | $0.50 | $25 | 512 |
| `claude-sonnet-5` (legacy) | $2 | $2.50 | $4 | $0.20 | $10 | 1,024 |
| `claude-opus-4-8` (legacy) | $5 | $6.25 | $10 | $0.50 | $25 | 1,024 |
| `claude-opus-4-7` (legacy) | $5 | $6.25 | $10 | $0.50 | $25 | 2,048 |
| `claude-opus-4-6` (legacy) | $5 | $6.25 | $10 | $0.50 | $25 | 4,096 |
| `claude-sonnet-4-6` (legacy) | $3 | $3.75 | $6 | $0.30 | $15 | 1,024 |
| `claude-haiku-4-5-20251001` (legacy) | $1 | $1.25 | $2 | $0.10 | $5 | 4,096 |

- Multipliers: 5-minute cache writes 1.25x base input, 1-hour writes 2x, cache reads 0.1x - except 0.05x on Claude Opus 5.5 and Claude Sonnet 5.5, and 0.025x on Claude Fable 5.1 and Claude Mythos 5.1. Batch API: 50% off.
- The cache minimum is not monotonic across generations (512 on the newest models, 4,096 on Opus 4.6 and Haiku 4.5). A prefix below it silently does not cache.
- Claude Opus 4.7 and later use a tokenizer that produces roughly 30% more tokens for the same text than earlier models. Recount when switching models.
- Thinking: `thinking: {type: "enabled", budget_tokens: N}` returns a 400 on Claude Opus 4.7 and later, Claude Sonnet 5 and later, Claude Haiku 5.5, and the Fable/Mythos 5.x models; it is deprecated on Opus 4.6 and Sonnet 4.6. Use adaptive thinking and `output_config.effort` (`low`, `medium`, `high`, `xhigh`, `max`; per-model support varies). Default effort is `medium` on Claude Opus 5.5 and Claude Haiku 5.5, `high` elsewhere. Thinking tokens bill as output and count toward `max_tokens`.
- Sampling parameters: `temperature`, `top_p`, and `top_k` are removed in API version `2026-10-21` (a 400 on every model). Earlier API versions reject non-default values on Claude 4.7 and later. The `anthropic` Python SDK 1.x dropped them as keyword arguments.
- Retirements: `claude-sonnet-4-5-20250929` retires 2026-11-30. `claude-sonnet-4-20250514`, `claude-opus-4-20250514`, `claude-opus-4-1-20250805`, and all Claude 3.x models are retired on the Claude API.

## OpenAI

Sources: `https://developers.openai.com/api/docs/pricing`, `.../guides/prompt-caching`, `.../models`, `.../deprecations`, `.../guides/migrate-to-responses`.

| Model ID | Input | Cached input | Cache write (30m / 12h) | Output |
|---|---|---|---|---|
| `gpt-6-astra` | $10 | $1.00 | $12.50 / $25 | $50 |
| `gpt-6.1-sol` | $2 | $0.10 | $2.50 / $5 | $10 |
| `gpt-6-luna` | $0.10 | $0.01 | $0.125 / $0.25 | $0.50 |

Short-context rates (input up to 272K tokens).

- Caching on GPT-5.6 and later: 1,024-token minimum; reads 0.1x input (0.05x on `gpt-6.1-sol`); writes 1.25x for the default 30-minute lifetime and 2.5x for 12 hours (Responses API only); up to four cache writes per request, one of them used by the implicit breakpoint unless `prompt_cache_options.mode` is `explicit`. Earlier models: minimum "varies by request settings", no cache-write rate listed on the pricing page, retention set by `prompt_cache_retention` (`in_memory` or `24h`; the SDK now marks it deprecated in favor of `prompt_cache_options.ttl`).
- Batch: roughly half the standard rates.
- Responses is recommended for all new projects; Chat Completions remains supported.
- Deprecated: `gpt-4o-2024-08-06`, `gpt-4o-2024-11-20`, `gpt-4o-mini-2024-07-18`, `gpt-4.1-2025-04-14`, and `gpt-4.1-mini-2025-04-14` are removed from the API on 2027-01-14 (notice 2026-10-14; replacement `gpt-6-luna`).

## Google Gemini API

Sources: `https://ai.google.dev/gemini-api/docs/pricing`, `.../generate-content/caching`, `.../models`, `.../libraries`.

| Model ID | Input | Cached input | Cache storage (per MTok per hour) | Output (includes thinking) |
|---|---|---|---|---|
| `gemini-4-argon` | $2.00, $4.00 from 2026-12-01 | $0.10, $0.20 from 2026-12-01 (implicit only) | not listed | $10, $20 from 2026-12-01 |
| `gemini-3.8-flash` | $0.75, $1.50 from 2027-01-01 | $0.075, $0.15 from 2027-01-01 | $0.50, $1.00 from 2027-01-01 | $3.75, $7.50 from 2027-01-01 |

- Implicit caching is on by default for Gemini 2.5 and newer. Minimum input: 4,096 tokens for `gemini-4-argon`, `gemini-3.8-flash`, `gemini-3.6-flash`, and `gemini-3.1-pro-preview`; 2,048 for Gemini 2.5 Flash and Pro.
- Explicit caching (`client.caches.create`) is not supported for `gemini-4-argon` and later. TTL defaults to 1 hour; the docs state no minimum or maximum TTL. Storage is billed for the TTL.
- Batch: 50% off.
- The `google-generativeai` package is deprecated (since 2025-11-30); use `google-genai`.

## SDK versions the examples were checked against (PyPI, 2026-10-26)

`anthropic` 2.3.0, `openai` 3.37.0, `google-genai` 2.33.0.
