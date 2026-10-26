# Output Optimization Techniques

Output tokens cost several times more than input tokens on every major provider (see [provider-facts.md](provider-facts.md)), and on reasoning models the hidden thinking or reasoning tokens bill as output too. The levers, in order:

1. Ask only for what the caller uses (schema design).
2. Enforce the format with the provider's structured-output feature, not with prose and retries.
3. Lower reasoning effort where the eval allows it.
4. Keep the output-token cap as a backstop, not a tuning knob.

## Schema design

**Verbose schema (avoid):**
```json
{
  "response": {
    "data": {
      "extracted_information": {
        "contact_details": {
          "full_name": "string",
          "email_address": "string",
          "phone_number": "string"
        }
      }
    },
    "metadata": {
      "extraction_timestamp": "string",
      "confidence_score": "number"
    }
  }
}
```

**Minimal schema (preferred):**
```json
{
  "name": "string",
  "email": "string",
  "phone": "string"
}
```

| Strategy | Example |
|----------|---------|
| Flat structure | Remove wrapper objects nobody reads |
| Only consumed fields | Drop timestamps, versions, and "confidence" fields the caller ignores |
| Enums for closed sets | `"sentiment": {"enum": ["positive", "negative", "neutral"]}` |
| Nullable over optional | `"phone": {"type": ["string", "null"]}` for predictable parsing |

Keep field names readable. Cryptic keys (`"s": "pos"`) save a token or two per field and make the model and every downstream reader guess.

## Enforce format with the API, not prose

| Provider | Feature |
|---|---|
| Claude | `output_config.format` with `type: "json_schema"` |
| OpenAI (Responses) | `text.format` with `type: "json_schema"`, `strict: true` |
| Gemini | `response_mime_type="application/json"` with `response_json_schema` |

Examples are in the provider guides. A schema-enforced response removes the "Return ONLY valid JSON" instruction, assistant prefill, stop-sequence guards, and retry-on-parse loops - and the tokens those retries burn. Keep the schema stable across requests: on Claude, changing it invalidates the prompt cache.

## Output length

### The cap is a backstop

`max_tokens` (Claude), `max_output_tokens` (OpenAI), and `max_output_tokens` in Gemini's config are hard limits on everything generated in the turn - on Claude and OpenAI that explicitly includes thinking or reasoning tokens. A cap sized to the visible answer (for example, 5-50 tokens for a classification) starves the reasoning and truncates the response, and a truncated response is a failed attempt you still pay for. Set the cap with generous headroom, stream large outputs, and treat a `max_tokens` / `max_output_tokens` stop as a failure to investigate, not a saving.

### Shorten what the model writes

- **Specify the output shape**, ideally with a short example of the target format. This is the most reliable way to shorten visible output.
- **Ask for no preamble** when the caller parses the result: "Answer directly, without introductions or restating the question."
- **Prefer qualitative length guidance** ("one short paragraph") over hard word caps, which can cut off needed detail on hard inputs.

### Shorten reasoning

Reasoning length is controlled by configuration, not prose:

| Provider | Control |
|---|---|
| Claude | `output_config.effort` (with adaptive thinking) |
| OpenAI | `reasoning.effort` |
| Gemini | `thinking_config` (`thinking_level` or `thinking_budget`, per model) |

Lower one step at a time and re-run the quality check; the quality cost differs by workload.

### Stop sequences

On Claude, a stop sequence is useful as an early-exit sentinel: tell the model to emit `<CANNOT_ANSWER>` when the input is out of scope and register it in `stop_sequences`, so it stops instead of explaining at length. Gemini's `GenerateContentConfig` also accepts `stop_sequences`. The OpenAI Responses API has no stop parameter.

## Format choice

Formats differ in tokens per value: JSON repeats keys on every record, CSV states them once, prose has no structure overhead. When the caller parses the output, the structured-output feature decides the format (JSON). When a human reads it, plain text or light Markdown. For bulk tabular extraction a human will open in a spreadsheet, CSV can be cheaper - measure both with the token counter on a realistic sample before switching.

## Checklist

- [ ] Schema contains only fields the caller reads
- [ ] Format enforced with the provider's structured-output feature
- [ ] No prose JSON instructions, prefill, or parse-retry loops left behind
- [ ] Output shape specified (with an example where useful)
- [ ] Reasoning effort swept on the eval, lowest passing level chosen
- [ ] Output cap set with headroom; cap-hit stops monitored
- [ ] Quality re-checked against the baseline (see quality-checklist.md)
