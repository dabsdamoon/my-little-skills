---
name: prompt-optimizer
description: "Cuts LLM API cost by restructuring prompts for prompt caching and trimming input and output tokens, across Claude, OpenAI, and Gemini. Use when asked to reduce token usage or API spend, make a prompt cache-friendly, raise a low cache hit rate, decide where cache breakpoints or TTLs go, or estimate what a prompt costs per request. Not for making a prompt clearer or better-behaved (use claude-api prompt-audit, or writing-skills:system-prompt-creator for a new system prompt); for a full cost pass over existing Claude API code, use claude-api cost-optimize."
---

# Prompt Optimizer

Lower what a production prompt costs per request without lowering what it produces. The levers, in order of typical payoff:

1. **Caching structure** - stable content first, dynamic content last, breakpoints and TTL matched to traffic. Cached input bills at a fraction of the normal rate on every major provider.
2. **Input trimming** - remove repetition, filler, and reference material most requests never read.
3. **Output control** - schema-enforced structured output, reasoning effort, and output shape.

## Scope and handoffs

This skill is about tokens, caching, and cost. It is not a prompt-quality review.

| Request | Use |
|---|---|
| "Make this prompt cheaper / cache better / use fewer tokens" (any provider) | This skill |
| "Is this prompt any good / outdated / make it work better" | The `claude-api` skill's `prompt-audit` subcommand (`/claude-api prompt-audit`) |
| "Write a system prompt for X" | `writing-skills:system-prompt-creator` |
| Full cost audit of existing Claude API code (usage reports, batch, effort sweeps, model choice) | `/claude-api cost-optimize` |

When trimming surfaces instructions that look dated or harmful rather than merely repeated, stop and hand them to `prompt-audit` - deciding whether an instruction is cruft is a quality judgment, and deleting by length is how optimization makes prompts worse.

## Volatile facts

Model IDs, prices, cache minimums, TTL options, and retirement dates are in [references/provider-facts.md](references/provider-facts.md), checked 2026-10-26. Do not quote numbers from memory; quote that file, and re-open its source pages when the user needs a current figure.

## Workflow

### Step 1: Collect

Ask for whatever is missing:

- **Provider and model** - caching rules, minimums, and prices are per model.
- **The prompt as sent** - tools, system prompt, examples, reference documents, and the per-request part (user input, retrieved context). The request-building code is better than a pasted string, because cache breakers hide in assembly code.
- **Traffic shape** - requests per day, and the typical gap between requests that share the same prefix (decides the TTL).
- **Usage data, if logged** - the provider's `usage` fields per request turn cache hit rate and input/output split from guesses into measurements.

### Step 2: Measure

Set `SKILL_DIR` to this skill directory. All three scripts accept text or a file.

```bash
# Static prefix, cache-breaking patterns, suggested breakpoints (no network)
python3 "$SKILL_DIR/scripts/cache_structure_validator.py" --prompt prompt.txt --provider claude --min-cache-tokens MIN

# Repetition, filler phrasing, cache structure score (no network)
python3 "$SKILL_DIR/scripts/prompt_analyzer.py" --input prompt.txt --min-cache-tokens MIN

# Token count and per-request / monthly input cost
python3 "$SKILL_DIR/scripts/token_counter.py" --provider estimate --file prompt.txt \
  --input-price IN --cache-write-price WRITE --cache-read-price READ --min-cache-tokens MIN
```

Replace `MIN` with the model's cache minimum and `IN`, `WRITE`, `READ` with its per-million-token prices from the facts file. The first two scripts and `--provider estimate` use about 4 characters per token; treat their numbers as approximate.

For exact counts, `token_counter.py --provider claude|openai|gemini --model MODEL` calls the provider's token-counting endpoint (no model inference). It needs that provider's SDK and API key in the environment. Supply the key for that one command through the project's secrets wrapper (for example `scripts/with-secrets.sh python3 "$SKILL_DIR/scripts/token_counter.py" ...`); do not export keys into the shell or print them. If the SDK is not installed, use `--provider estimate` rather than installing packages on the fly.

### Step 3: Restructure for caching

Every provider caches a **prefix**: any change at position N invalidates everything after N. So:

1. Order content by stability: tools, then instructions and fixed examples, then shared reference documents, then per-session data, then the per-request input.
2. Move anything that changes per request (dates, IDs, user names, retrieved passages) after the last stable block.
3. Serialize deterministically (sorted JSON keys, stable tool order, no conditional sections in the prefix).
4. Place breakpoints at stability boundaries and choose the TTL from the gap between requests.

Provider mechanics differ - explicit vs implicit breakpoints, TTL options, write premiums, storage fees:

- Claude: [references/providers/claude.md](references/providers/claude.md)
- OpenAI: [references/providers/openai.md](references/providers/openai.md)
- Gemini: [references/providers/gemini.md](references/providers/gemini.md)

Detailed structure patterns and anti-patterns: [references/input-optimization.md](references/input-optimization.md).

### Step 4: Trim input

- Consolidate instructions stated more than once.
- Remove filler phrasing ("I would like you to", "please make sure to"); keep every reason and constraint.
- Reduce near-duplicate examples to a few varied ones.
- Cache reference material that most requests read; retrieve material that few requests need.
- Shrink tool overhead by loading fewer tools and keeping the list stable - not by cutting tool descriptions to one-liners, which causes wrong calls.

Do not use lossy token-dropping compressors or invented abbreviations; both trade small savings for worse instruction following.

### Step 5: Control output

Output tokens cost several times more than input, and reasoning tokens bill as output.

- Request only the fields the caller reads, and enforce the schema with the provider's structured-output feature instead of prose instructions and parse retries.
- Lower reasoning effort (Claude `output_config.effort`, OpenAI `reasoning.effort`, Gemini `thinking_config`) one step at a time against an eval.
- Specify the output shape, ideally with an example, to shorten visible output.
- Treat the output-token cap as a backstop with headroom: on Claude and OpenAI it includes thinking or reasoning tokens, so a tight cap truncates the answer and wastes the call.
- Do not set `temperature` for Claude: sampling parameters are removed in the current Anthropic API version.

Details: [references/output-optimization.md](references/output-optimization.md).

### Step 6: Validate

1. **Cache works**: send the same request twice and read the provider's usage fields on the second response - Claude `usage.cache_read_input_tokens`, OpenAI `usage.input_tokens_details.cached_tokens`, Gemini `usage_metadata.cached_content_token_count`. Zero means the prefix changed or is below the minimum.
2. **Quality held**: compare original and optimized prompts on the same representative inputs. Every run costs money - estimate it and get the user's approval first. Checklist and rollback criteria: [references/quality-checklist.md](references/quality-checklist.md).
3. **Revert** any change that saves tokens but loses quality. The goal is lower cost per completed task, not a shorter prompt.

## Report template

```markdown
## Prompt Cost Optimization Report

**Provider / model**: [from facts file]  **Traffic**: [requests/day, gap between requests]
**Prices used**: [per MTok, from provider-facts.md, checked YYYY-MM-DD]

| Metric | Original | Optimized |
|---|---|---|
| Input tokens per request | X | Y |
| Static (cacheable) prefix | A | B |
| Meets cache minimum | yes/no | yes/no |
| Input cost per request (cache hit) | $ | $ |
| Monthly input cost at N requests | $ | $ |

### Changes
1. [Change] - [tokens or cost effect]

### Cache configuration
- Breakpoints: [where]
- TTL: [choice and why, from the request gap]

### Verification
- Second-request cached tokens: [value]
- Quality comparison: [N inputs, result]

### Not changed
- [Instruction or section left alone, and why - e.g. handed to prompt-audit]
```

## Common pitfalls

| Pitfall | Fix |
|---|---|
| Timestamp or user ID in the system prompt | Move it into the per-request message |
| Breakpoint after unique per-request content | Put it at the end of the shared portion |
| Prefix just under the model's minimum | It silently does not cache; check the facts file |
| Changing schema, tools, effort, or model mid-conversation | Each invalidates part or all of the cache; pin them per route |
| Trimming reasons and context to save tokens | Restore them; cost per completed task goes up when quality drops |
| Optimizing before the prompt works | Get it correct first, then make it cheap |
