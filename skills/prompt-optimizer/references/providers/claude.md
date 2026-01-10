# Claude/Anthropic Optimization Guide

## Prompt Caching

Claude's prompt caching reduces input costs by up to 90% and latency by up to 85%.

### How It Works

1. Mark cacheable content with `cache_control`
2. First request: cache write (25% premium)
3. Subsequent requests: cache read (90% discount)
4. Cache TTL: 5 minutes (refreshed on each hit)

### Requirements

| Model | Minimum Tokens |
|-------|----------------|
| Sonnet | 1,024 |
| Haiku | 1,024 |
| Opus | 2,048 |

### Implementation

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": """You are a helpful assistant specialized in...""",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[
        {"role": "user", "content": user_query}  # Dynamic content
    ]
)
```

### Multi-Component Caching

Cache up to 4 breakpoints:

```python
system=[
    {
        "type": "text",
        "text": "System instructions...",
        "cache_control": {"type": "ephemeral"}  # Breakpoint 1
    },
    {
        "type": "text",
        "text": "Large reference document...",
        "cache_control": {"type": "ephemeral"}  # Breakpoint 2
    },
    {
        "type": "text",
        "text": "Few-shot examples...",
        "cache_control": {"type": "ephemeral"}  # Breakpoint 3
    }
]
```

### Best Practices

1. **Static first, dynamic last**: Place all cacheable content before dynamic content
2. **Natural breakpoints**: Set cache_control at logical boundaries
3. **Multi-turn optimization**: Cache system prompt + conversation prefix
4. **Tools caching**: Cache tool definitions separately

### Monitoring

Check cache effectiveness via response:

```python
usage = response.usage
print(f"Cache write: {usage.cache_creation_input_tokens}")
print(f"Cache read: {usage.cache_read_input_tokens}")
print(f"Uncached: {usage.input_tokens}")
```

### Pricing (per 1M tokens, Sonnet)

| Type | Cost |
|------|------|
| Regular input | $3.00 |
| Cache write | $3.75 |
| Cache read | $0.30 |

**Break-even**: ~2 requests with same cached content

---

## Token-Efficient Tool Use

Built into Claude 4 models. Reduces tool-related output tokens by 14-70%.

### Behavior

- Tool call XML is condensed
- Function names and parameters optimized
- No configuration needed (automatic)

### Note for Claude 3.x

Requires beta header:
```python
client.messages.create(
    model="claude-3-7-sonnet-20250219",
    betas=["token-efficient-tools-2025-02-19"],
    ...
)
```

---

## Extended Thinking

For complex tasks, extended thinking improves quality but affects caching.

### Impact on Caching

- Thinking blocks stripped when new non-tool content added
- Consider trade-off: quality vs cache efficiency
- Best for single-turn complex reasoning

### Implementation

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[...]
)
```

---

## Structured Outputs

Claude supports JSON mode for reliable structured responses.

### Implementation

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="Return valid JSON only.",
    messages=[
        {
            "role": "user",
            "content": "Extract: name, email, phone from this text..."
        }
    ]
)
```

### Tips

1. Specify schema in system prompt
2. Use examples for complex structures
3. Request minimal fields only
4. Consider YAML for simpler structures (fewer tokens)

---

## Claude-Specific Prompt Tips

### Concise Instructions

Claude responds well to direct, concise instructions:

```
# Verbose (avoid)
I would like you to please help me by summarizing the following text.
Please make sure to capture the main points and key details.

# Concise (preferred)
Summarize this text. Include main points and key details.
```

### XML Tags

Claude excels with XML-structured prompts:

```xml
<instructions>
Analyze the document and extract key information.
</instructions>

<document>
{document_content}
</document>

<output_format>
- Title
- Main points (3-5)
- Conclusion
</output_format>
```

### System vs User Prompt

- **System**: Role, constraints, format requirements
- **User**: Task-specific content, context, queries

Keep system prompt stable for caching; vary user content.
