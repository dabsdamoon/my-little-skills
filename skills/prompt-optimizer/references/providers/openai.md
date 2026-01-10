# OpenAI Optimization Guide

## Automatic Prompt Caching

OpenAI automatically caches prompts. No explicit configuration needed.

### How It Works

1. Repeated prompt prefixes are automatically cached
2. 50% discount on cached tokens
3. Works with consistent request patterns
4. No TTL management required

### Optimization Strategy

Structure prompts with stable prefixes:

```
[STABLE PREFIX - automatically cached]
System instructions, role definition, examples...

[VARIABLE SUFFIX - not cached]
User query, dynamic context...
```

### Monitoring

Check `usage` in response:
```python
response.usage.prompt_tokens_details.cached_tokens
```

---

## Structured Outputs

Guarantee valid JSON matching your schema.

### Implementation

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract contact information."},
        {"role": "user", "content": text}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "contact_info",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": ["string", "null"]}
                },
                "required": ["name", "email", "phone"],
                "additionalProperties": False
            }
        }
    }
)
```

### Schema Caching

First request with new schema incurs latency (schema compilation).
Subsequent requests are fast.

- Simple schemas: <10 seconds first request
- Complex schemas: up to 60 seconds first request

### Tips

1. **Minimal schemas**: Only include required fields
2. **Strict mode**: Use `strict: True` for guaranteed compliance
3. **Nullable fields**: Use `["string", "null"]` for optional fields
4. **No additionalProperties**: Always set to `False` for efficiency

---

## Function Calling Optimization

### Minimal Tool Definitions

```python
# Verbose (avoid)
tools = [{
    "type": "function",
    "function": {
        "name": "search_database",
        "description": "This function searches the database for records matching the query. It returns a list of matching records with their details.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "The search query string to use when searching the database"
                }
            }
        }
    }
}]

# Concise (preferred)
tools = [{
    "type": "function",
    "function": {
        "name": "search_db",
        "description": "Search database records",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}]
```

### Parallel Tool Calls

Enable for independent operations:
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    parallel_tool_calls=True
)
```

---

## Pricing (per 1M tokens, GPT-4o)

| Type | Cost |
|------|------|
| Input | $2.50 |
| Cached input | $1.25 |
| Output | $10.00 |

---

## OpenAI-Specific Tips

### System Message Optimization

Keep system messages concise:

```
# Verbose
You are an AI assistant created by [Company]. Your role is to help users
with their questions. You should always be helpful, harmless, and honest.
When answering questions, provide accurate information.

# Concise
You are [Company]'s assistant. Be helpful, accurate, and concise.
```

### Few-Shot Examples

Place in system message for caching:

```python
messages = [
    {
        "role": "system",
        "content": """Classify sentiment as positive/negative/neutral.

Examples:
"Great product!" -> positive
"Terrible service" -> negative
"It works" -> neutral"""
    },
    {"role": "user", "content": text_to_classify}
]
```

### Temperature for Structured Output

Use `temperature=0` for deterministic structured outputs.

### Max Tokens

Set appropriate `max_tokens` to prevent over-generation:
- Classification: 10-50 tokens
- Extraction: 100-500 tokens
- Summaries: 200-1000 tokens
