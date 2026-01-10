# Output Optimization Techniques

Strategies to reduce output tokens and improve response structure.

## Structured Output Design

### JSON Schema Optimization

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

**Savings: ~70% on schema, ~50% on output**

### Field Optimization

| Strategy | Example | Impact |
|----------|---------|--------|
| Short field names | `full_name` → `name` | -2 tokens/field |
| Flat structure | Remove unnecessary nesting | -20-40% |
| Enums over strings | `"sentiment": "pos"` | -5 tokens |
| Nullable vs optional | Use `null` instead of omitting | Predictable parsing |
| No metadata | Remove timestamps, versions | -10-20% |

### Enum Design

```json
// Verbose
{"sentiment": "positive", "confidence": "high", "category": "product_review"}

// Concise
{"s": "pos", "c": "hi", "cat": "prod"}

// With instruction
"Use abbreviations: s=sentiment (pos/neg/neu), c=confidence (hi/med/lo)"
```

---

## Response Format Control

### Stop Sequences

Prevent over-generation:

```python
# Claude
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    stop_sequences=["\n\nNote:", "\n\nExplanation:", "---"]
)

# OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    stop=["\n\nNote:", "\n\nExplanation:"]
)
```

### Max Tokens Guidelines

| Task Type | Recommended Max |
|-----------|-----------------|
| Classification | 10-50 |
| Yes/No questions | 5-20 |
| Entity extraction | 100-500 |
| Short summaries | 200-500 |
| Long summaries | 500-2000 |
| Code generation | 500-4000 |
| General Q&A | 500-2000 |

**Tip**: Set max_tokens slightly above expected output. Monitor for truncation.

### Length Instructions

Be explicit about desired length:

```
# Vague (unpredictable length)
Summarize this article.

# Specific (controlled length)
Summarize in 2-3 sentences (50-75 words max).
```

---

## Format Comparison

| Format | Tokens | Use Case |
|--------|--------|----------|
| Plain text | Baseline | Human reading |
| Markdown | +10-20% | Documentation, reports |
| JSON | +20-40% | API integration |
| YAML | +10-25% | Config, human-readable structured |
| XML | +30-50% | Legacy systems |
| CSV | -10-20% | Tabular data |

### When to Use Each

**Plain text**: Chatbots, simple Q&A
```
The answer is 42.
```

**Markdown**: Documentation, user-facing reports
```markdown
## Summary
The main point is...
```

**JSON**: APIs, programmatic processing
```json
{"answer": 42, "confidence": 0.95}
```

**YAML**: Configuration, human-editable structured data
```yaml
answer: 42
confidence: 0.95
```

**CSV**: Batch extraction, spreadsheet export
```
name,email,phone
John,john@example.com,555-1234
```

---

## Token-Efficient Patterns

### 1. Instruction to Be Concise

Add to system prompt:
```
Be concise. No preamble or explanations unless asked.
```

### 2. Direct Answers Only

```
# Verbose response (typical)
That's a great question! Let me help you with that.
The capital of France is Paris. Paris has been the
capital since... [continues]

# Concise response (instructed)
Paris
```

Instruction:
```
Answer directly. No introductions, acknowledgments, or elaborations.
```

### 3. Structured Response Templates

Force specific structure:
```
Respond using ONLY this format:
ANSWER: [your answer]
CONFIDENCE: [high/medium/low]
```

### 4. Thinking vs Output Separation

For Claude with extended thinking:
```
Use thinking for analysis. Keep final output under 100 words.
```

---

## Provider-Specific Output Features

### Claude

- Streaming for long responses
- Stop sequences (up to 4)
- JSON mode via instruction

### OpenAI

- Structured outputs (schema enforcement)
- JSON mode
- Function calling for structured data
- Logprobs for confidence

### Gemini

- JSON mode (`response_mime_type`)
- Schema enforcement
- Grounding with citations

---

## Quick Reference: Output Checklist

- [ ] Use minimal JSON schema (flat, short names)
- [ ] Set appropriate max_tokens
- [ ] Add stop sequences for over-generation
- [ ] Specify desired length explicitly
- [ ] Choose format based on use case
- [ ] Add "be concise" instruction
- [ ] Remove metadata fields not needed
- [ ] Use enums instead of long strings
- [ ] Test output consistency
