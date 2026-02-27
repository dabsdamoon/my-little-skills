# Google Gemini Optimization Guide

## Context Caching

Gemini offers explicit context caching with configurable TTL.

### How It Works

1. Create cached content with `CachedContent.create()`
2. Specify TTL (up to 1 hour)
3. Use cached content across multiple requests
4. Pay storage costs for cached content

### Requirements

- Minimum: 32,768 tokens
- Best for: Large documents, knowledge bases, long conversations

### Implementation

```python
import google.generativeai as genai
import datetime

# Create cached content
cache = genai.caching.CachedContent.create(
    model="gemini-1.5-pro",
    contents=[
        {
            "role": "user",
            "parts": [large_document_content]
        }
    ],
    ttl=datetime.timedelta(hours=1),
    display_name="my-cached-content"
)

# Use cached content
model = genai.GenerativeModel.from_cached_content(cache)
response = model.generate_content("Summarize the key points.")
```

### Managing Cache

```python
# List cached content
for cache in genai.caching.CachedContent.list():
    print(cache.name, cache.expire_time)

# Delete cached content
cache.delete()
```

### Pricing

| Type | Cost (per 1M tokens) |
|------|---------------------|
| Input | $1.25 |
| Cached input | $0.3125 |
| Output | $5.00 |
| Cache storage | $1.00/hour |

**Break-even**: ~4 requests/hour with large cached content

---

## System Instructions

Gemini supports system instructions that persist across turns.

### Implementation

```python
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction="You are a helpful coding assistant. Always provide concise code examples."
)

response = model.generate_content("How do I read a file in Python?")
```

### Combining with Cache

```python
# Cache large reference, use system instruction for behavior
cache = genai.caching.CachedContent.create(
    model="gemini-1.5-pro",
    contents=[api_documentation],
    system_instruction="You are an API expert. Answer questions using the provided documentation.",
    ttl=datetime.timedelta(hours=1)
)
```

---

## Structured Output

Gemini supports JSON mode and schema enforcement.

### JSON Mode

```python
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config={"response_mime_type": "application/json"}
)

response = model.generate_content(
    "Extract name, email, phone from: John Doe, john@example.com, 555-1234"
)
```

### With Schema

```python
import typing_extensions as typing

class ContactInfo(typing.TypedDict):
    name: str
    email: str
    phone: str | None

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": ContactInfo
    }
)
```

---

## Function Calling

### Minimal Declarations

```python
get_weather = genai.protos.FunctionDeclaration(
    name="get_weather",
    description="Get weather for location",
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=[get_weather]
)
```

---

## Gemini-Specific Tips

### Long Context Optimization

Gemini excels with long context (up to 2M tokens). For large documents:

1. Use context caching for repeated queries
2. Place important content at start and end (avoid "lost in middle")
3. Use clear section markers

### Multimodal Prompts

For image/video analysis, structure prompts clearly:

```python
response = model.generate_content([
    "Analyze this image and extract:",
    "1. Main subject",
    "2. Text content",
    "3. Key objects",
    image_part
])
```

### Safety Settings

Adjust safety settings to reduce unnecessary refusals:

```python
from google.generativeai.types import HarmCategory, HarmBlockThreshold

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
)
```

### Grounding

Use Google Search grounding for factual queries:

```python
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=[genai.protos.Tool(google_search_retrieval={})]
)
```
