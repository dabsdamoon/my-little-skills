---
name: prompt-optimizer
description: "Optimize prompts for production LLM applications by reducing token usage, maximizing cache efficiency, and improving output structure while preserving quality. Use when asked to optimize prompts, reduce API costs, improve prompt caching, minimize token usage, design cache-friendly prompts, or enhance prompt efficiency for Claude, OpenAI, Gemini, or other LLM providers. Supports three tiers: guidance-only, minimal scripts (token counting), or full analysis with Python tools."
---

# Prompt Optimizer

Optimize prompts for production LLM applications targeting:
- **Input efficiency**: Minimize tokens, maximize cache utilization
- **Output efficiency**: Structured outputs, response format optimization
- **Quality preservation**: Maintain effectiveness during optimization

## Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Provider   │───▶│    Tier     │───▶│   Analyze   │───▶│  Optimize   │───▶│  Validate   │
│  Selection  │    │  Selection  │    │   Prompt    │    │   Prompt    │    │   Quality   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Step 1: Provider Selection

Ask the user:

**"Which LLM provider are you optimizing for?"**

| Option | Description |
|--------|-------------|
| (1) Claude/Anthropic | Explicit caching, token-efficient tools |
| (2) OpenAI | Automatic caching, structured outputs |
| (3) Google Gemini | Context caching API |
| (4) Provider-agnostic | General optimization techniques |
| (5) Multiple providers | Cross-compatible optimization |

Based on selection, load provider-specific guidance:
- **Claude**: See [references/providers/claude.md](references/providers/claude.md)
- **OpenAI**: See [references/providers/openai.md](references/providers/openai.md)
- **Gemini**: See [references/providers/gemini.md](references/providers/gemini.md)

**For deep provider-specific optimization**, suggest using the subagent-creator skill to create a dedicated optimization agent.

---

## Step 2: Tier Selection

Ask the user:

**"Which optimization tier would you like to use?"**

| Tier | Description | Requirements |
|------|-------------|--------------|
| **Guidance Only** | Manual optimization using best practices | None |
| **Minimal Scripts** | Token counting + cache analysis | Python + tiktoken/anthropic |
| **Full Analysis** | Comprehensive automated analysis | Python + additional packages |

### Dependency Warnings

**Minimal tier:**
```bash
pip install tiktoken anthropic  # ~50MB
```

**Full tier:**
```bash
pip install tiktoken anthropic  # For token counting
# Additional for advanced analysis (optional):
# pip install transformers torch  # ~2GB, for entropy analysis
```

---

## Step 3: Analyze Current Prompt

### 3.1 Collect Prompt Components

Request from user:
1. **System prompt**: Role definition, instructions, rules
2. **User message template**: With variable placeholders
3. **Examples**: Few-shot examples if used
4. **Expected output format**: JSON schema, markdown, etc.

### 3.2 Analysis Checklist

#### Input Efficiency
- [ ] Token count (by provider tokenizer)
- [ ] Redundant instructions (repeated concepts)
- [ ] Verbose phrasing (can be condensed)
- [ ] Static vs dynamic content ratio
- [ ] Cache-friendliness (static prefix length)

#### Output Efficiency
- [ ] Response format clarity
- [ ] Structured output potential
- [ ] Stop sequence opportunities
- [ ] Max token appropriateness

#### Quality Indicators
- [ ] Clear task definition
- [ ] Unambiguous instructions
- [ ] Representative examples
- [ ] Edge case handling

### 3.3 Token Counting (Minimal/Full Tier)

Run the token counter script:

```bash
python scripts/token_counter.py "<prompt_text>" --provider claude
# Or from file:
python scripts/token_counter.py --file prompt.txt --provider all
```

Output includes:
- Token count per provider
- Cost estimate per request
- Cache-eligible prefix analysis
- Monthly cost projection

### 3.4 Full Analysis (Full Tier)

Run the prompt analyzer:

```bash
python scripts/prompt_analyzer.py --input prompt.txt
```

Output includes:
- Redundancy detection (repeated phrases)
- Verbosity analysis (condensable patterns)
- Cache structure analysis
- Overall optimization score

---

## Step 4: Optimize

### 4.1 Input Optimization

See [references/input-optimization.md](references/input-optimization.md) for detailed techniques.

**Quick Reference:**

| Strategy | Token Savings | Implementation |
|----------|---------------|----------------|
| Remove redundancy | 10-30% | Consolidate repeated instructions |
| Condense phrasing | 5-15% | "You must always" → "Always" |
| Cache-friendly structure | 90% cost reduction | Static prefix + dynamic suffix |
| Strategic examples | Variable | Quality over quantity |

**Cache-Friendly Structure Pattern:**

```
[STATIC PREFIX - cached]
You are an expert {role}. Your task is to {mission}.

Rules:
1. Always {rule1}
2. Never {rule2}

Output format: {format_spec}

Examples:
{fixed_examples}

--- END CACHED CONTENT ---

[DYNAMIC SUFFIX - not cached]
Context: {user_context}
Query: {user_query}
```

### 4.2 Output Optimization

See [references/output-optimization.md](references/output-optimization.md) for detailed techniques.

**Quick Reference:**

| Strategy | Token Savings | Implementation |
|----------|---------------|----------------|
| JSON schema enforcement | 20-40% | Structured outputs API |
| Minimal field design | Variable | Only request needed fields |
| Stop sequences | 5-20% | Prevent trailing content |
| Concise instruction | 10-30% | "Be concise. No preamble." |

**Minimal JSON Schema Example:**

```json
{
  "type": "object",
  "properties": {
    "answer": {"type": "string"},
    "confidence": {"type": "number"}
  },
  "required": ["answer"],
  "additionalProperties": false
}
```

### 4.3 Provider-Specific Tips

**Claude:**
- Use `cache_control` for prompts >1024 tokens
- Token-efficient tool use is automatic in Claude 4
- Consider extended thinking for complex tasks

**OpenAI:**
- Caching is automatic (consistent prefixes)
- Use structured outputs for JSON
- Set `temperature=0` for deterministic output

**Gemini:**
- Context caching for prompts >32K tokens
- Longer TTL options (up to 1 hour)
- Storage costs apply to cached content

---

## Step 5: Validate

### 5.1 Quality Preservation Checklist

See [references/quality-checklist.md](references/quality-checklist.md) for complete guide.

Before deploying optimized prompt:

- [ ] **Semantic equivalence**: Same-quality outputs on test cases
- [ ] **Edge case handling**: Unusual inputs still work
- [ ] **Format consistency**: Output structure maintained
- [ ] **No instruction loss**: Critical behaviors preserved

### 5.2 A/B Comparison

Run both prompts on 5-10 representative inputs:

| Input | Original Output | Optimized Output | Quality Match? |
|-------|-----------------|------------------|----------------|
| Test 1 | ... | ... | Yes/No |
| Test 2 | ... | ... | Yes/No |

**Pass criteria**: >95% semantic match

### 5.3 Cost-Quality Trade-off

Calculate:
```
Token reduction = (original - optimized) / original × 100%
Quality score = matches / total_tests × 100%
Monthly savings = token_reduction × requests/month × cost/token
```

**If quality drops >5%**, revert specific optimizations.

### 5.4 Cache Structure Validation (Minimal/Full Tier)

```bash
python scripts/cache_structure_validator.py --prompt optimized_prompt.txt --provider claude
```

Validates:
- Static prefix meets minimum threshold
- No cache-breaking patterns in static section
- Dynamic content positioned correctly

---

## Optimization Report Template

After optimization, provide:

```markdown
## Prompt Optimization Report

### Summary
| Metric | Original | Optimized | Change |
|--------|----------|-----------|--------|
| Total tokens | X | Y | -Z% |
| Cache-eligible | A | B | +C% |
| Est. cost/request | $X.XX | $Y.YY | -Z% |

### Changes Made
1. [Change description] - saved ~N tokens
2. [Change description] - saved ~N tokens
3. [Change description] - improved cache efficiency

### Cache Configuration
- Provider: [Claude/OpenAI/Gemini]
- Static prefix: X tokens (Y% of prompt)
- Recommended cache_control placement: [position]
- Estimated cache hit rate: Z%

### Quality Verification
- Test cases passed: X/Y
- Semantic equivalence: Verified
- Edge cases: Verified

### Monthly Cost Projection (10,000 requests)
| Scenario | Cost |
|----------|------|
| Without caching | $XX.XX |
| With caching (95% hit) | $YY.YY |
| **Savings** | **$ZZ.ZZ** |

### Optimized Prompt
[Full optimized prompt here]
```

---

## Quick Reference

### When to Use Each Tier

| Scenario | Recommended Tier |
|----------|------------------|
| One-off optimization | Guidance Only |
| Regular prompt tuning | Minimal Scripts |
| Production cost analysis | Full Analysis |
| Learning/exploration | Guidance Only |

### Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Over-compression | Keep critical context; test quality |
| Breaking cache | Ensure static content stays static |
| Ignoring provider differences | Use provider-specific techniques |
| Optimizing prematurely | Optimize after prompt is working |
| Verbose placeholders | Use short variable names |

### Cache Minimums by Provider

| Provider | Minimum Tokens | TTL |
|----------|----------------|-----|
| Claude (Sonnet) | 1,024 | 5 min |
| Claude (Opus) | 2,048 | 5 min |
| OpenAI | 0 (automatic) | Auto |
| Gemini | 32,768 | Up to 1 hour |

---

## References

- [Input Optimization Techniques](references/input-optimization.md)
- [Output Optimization Techniques](references/output-optimization.md)
- [Quality Preservation Checklist](references/quality-checklist.md)
- [Claude-Specific Guide](references/providers/claude.md)
- [OpenAI-Specific Guide](references/providers/openai.md)
- [Gemini-Specific Guide](references/providers/gemini.md)
