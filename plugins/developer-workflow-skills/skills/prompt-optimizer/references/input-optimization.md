# Input Optimization Techniques

Strategies to reduce input tokens while preserving prompt effectiveness.

## Token Compression Strategies

### 1. Remove Redundancy

Identify and eliminate repeated concepts:

**Before (redundant):**
```
You are a helpful assistant. You must always be helpful.
Remember to be helpful in your responses. Your goal is to help users.
When responding, make sure to provide helpful information.
```

**After (concise):**
```
You are a helpful assistant.
```

**Savings: ~80%**

### 2. Condense Phrasing

Replace verbose constructions with concise equivalents:

| Verbose | Concise | Savings |
|---------|---------|---------|
| "You must always" | "Always" | 2 tokens |
| "Please make sure to" | "" (implied) | 4 tokens |
| "In order to" | "To" | 2 tokens |
| "It is important that" | "" (implied) | 4 tokens |
| "You should remember to" | "" (implied) | 4 tokens |
| "Make sure that you" | "" (implied) | 4 tokens |
| "I would like you to" | "" (implied) | 5 tokens |
| "Could you please" | "" (implied) | 3 tokens |
| "at this point in time" | "now" | 4 tokens |
| "due to the fact that" | "because" | 4 tokens |
| "in the event that" | "if" | 3 tokens |

**Example:**
```
# Before
I would like you to please make sure to analyze the following text
and provide a comprehensive summary of the main points.

# After
Analyze this text. Summarize main points.

# Savings: ~60%
```

### 3. Abbreviations (Use Sparingly)

Define once, use throughout:

```
Definitions: usr=user, req=request, resp=response, ctx=context

When usr sends req with ctx, generate resp following these rules:
```

**Warning**: May reduce clarity. Test thoroughly.

### 4. Strategic Examples

Quality over quantity. Remove redundant examples:

**Before (redundant examples):**
```
Examples:
1. "Great product!" -> positive
2. "Love it!" -> positive
3. "Amazing quality!" -> positive
4. "Terrible" -> negative
5. "Awful service" -> negative
6. "It's okay" -> neutral
```

**After (diverse examples):**
```
Examples:
- "Great product!" -> positive
- "Terrible service" -> negative
- "It's okay" -> neutral
```

**Savings: ~50%**

---

## Cache-Friendly Structure

### The Pattern

```
┌─────────────────────────────────┐
│     STATIC PREFIX (cached)      │
│  - System instructions          │
│  - Role definition              │
│  - Format requirements          │
│  - Fixed examples               │
│  - Reference documents          │
├─────────────────────────────────┤
│     DYNAMIC SUFFIX (not cached) │
│  - User context                 │
│  - Current query                │
│  - Variable data                │
└─────────────────────────────────┘
```

### Implementation Template

```
[SYSTEM INSTRUCTIONS - STATIC]
You are an expert {role}. Your task is to {mission}.

[RULES - STATIC]
1. Always {rule1}
2. Never {rule2}
3. Format output as {format}

[EXAMPLES - STATIC]
Input: {example1_input}
Output: {example1_output}

Input: {example2_input}
Output: {example2_output}

[REFERENCE - STATIC, if needed]
{large_reference_document}

--- END CACHED CONTENT ---

[USER CONTEXT - DYNAMIC]
{user_provided_context}

[QUERY - DYNAMIC]
{user_query}
```

### Anti-Patterns (Avoid)

**1. Dynamic content in static section:**
```
# BAD - timestamp breaks cache
You are an assistant. Today is {current_date}.
System version: {version}

# GOOD - no dynamic content in static section
You are an assistant.
```

**2. User ID before instructions:**
```
# BAD - unique per user
User ID: {user_id}
You are a helpful assistant...

# GOOD - user info after static content
You are a helpful assistant...
User ID: {user_id}
```

**3. Random ordering:**
```
# BAD - inconsistent order
{context}
{instructions}
{examples}

# GOOD - consistent order
{instructions}
{examples}
{context}
```

---

## Advanced: LLMLingua Compression

Microsoft Research tool achieving up to 20x compression.

### How It Works

1. Uses small model (e.g., LLaMA-7B) to calculate token importance
2. Removes low-information tokens
3. Preserves semantic meaning

### Example

**Original (100 tokens):**
```
I would like you to carefully analyze the following text document
and provide me with a comprehensive and detailed summary that captures
all of the main points and key information contained within the text.
```

**Compressed (~30 tokens):**
```
analyze text document provide summary main points key information
```

### When to Use

- Very long prompts (>4000 tokens)
- High-volume applications
- Cost-sensitive deployments
- RAG with large contexts

### Risks

- Quality degradation on nuanced tasks
- Edge case failures
- Requires validation testing
- Additional infrastructure (compression model)

### Implementation

```python
from llmlingua import PromptCompressor

compressor = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
    use_llmlingua2=True
)

compressed = compressor.compress_prompt(
    original_prompt,
    rate=0.5,  # 50% compression
    force_tokens=["important", "critical"]  # Preserve these
)
```

---

## Quick Reference: Compression Checklist

- [ ] Remove duplicate/redundant phrases
- [ ] Replace verbose constructions
- [ ] Consolidate similar examples
- [ ] Place static content before dynamic
- [ ] Remove unnecessary pleasantries
- [ ] Use concise variable names
- [ ] Remove filler words
- [ ] Test quality after each change
