# Input Optimization Techniques

Cut what the model is billed for on every request without cutting what it needs to know. Caching usually saves far more than trimming, so restructure for caching first, then trim.

The rule that keeps trimming safe: **remove repetition and filler, never context.** Audience, product facts, constraints, and the reasons behind them are what only the author knows; deleting them makes outputs worse and often longer. Judging whether an instruction is dated or harmful is a prompt-quality question - hand it to the `claude-api` skill's `prompt-audit` subcommand rather than deleting by length.

## Cache-friendly structure

Every provider caches a prefix. Order content by how often it changes:

```
┌──────────────────────────────────────┐
│ Never changes                        │
│  - tool definitions                  │
│  - system instructions and context   │
│  - fixed examples                    │
│  - shared reference documents        │
├──── cache breakpoint ────────────────┤
│ Changes per session                  │
│  - user profile, account settings    │
├──── cache breakpoint (optional) ─────┤
│ Changes per request                  │
│  - retrieved passages                │
│  - the current question              │
│  - timestamps, request IDs           │
└──────────────────────────────────────┘
```

Template:

```
[STABLE - cached]
<instructions>
{what the task is, who the output is for, constraints and why they exist}
</instructions>

<examples>
{fixed, varied examples}
</examples>

<reference>
{shared documents every request needs}
</reference>

--- cache breakpoint ---

[PER REQUEST - not cached]
<context>{retrieved or user-specific context}</context>
<question>{current question}</question>
```

### Anti-patterns

**Dynamic content in the stable section:**
```
# BAD - the date changes the prefix every day
You are a support assistant. Today is {current_date}.

# GOOD - pass the date with the request
You are a support assistant.
...
<context>Today is {current_date}.</context>
```

**User-specific data before instructions:**
```
# BAD - a different prefix per user, nothing shared
User ID: {user_id}
<instructions>...</instructions>

# GOOD
<instructions>...</instructions>
...
<context>User ID: {user_id}</context>
```

**Unstable ordering:** tools or sections assembled from a set, a dict without sorted keys, or conditional sections (`if flag: prompt += ...`) produce a different prefix per combination. Serialize deterministically and move optional sections after the breakpoint.

## Trimming

### 1. Remove repetition

The same instruction stated three ways costs three times and makes the model reconcile the wordings.

**Before:**
```
You are a helpful assistant. You must always be helpful.
Remember to be helpful in your responses. Your goal is to help users.
```

**After:**
```
You are a helpful assistant.
```

### 2. Condense filler phrasing

| Verbose | Concise |
|---------|---------|
| "You must always" | "Always" |
| "Please make sure to" | (drop) |
| "In order to" | "To" |
| "I would like you to" | (drop) |
| "Could you please" | (drop) |
| "at this point in time" | "now" |
| "due to the fact that" | "because" |
| "in the event that" | "if" |

Do not condense a sentence that carries a reason or a constraint ("because refunds over $500 need approval") into a bare rule; the reason is what lets the model handle cases the rule does not name.

### 3. Fewer, more varied examples

Several near-identical examples cost tokens and teach one narrow pattern.

**Before:**
```
1. "Great product!" -> positive
2. "Love it!" -> positive
3. "Amazing quality!" -> positive
4. "Terrible" -> negative
5. "Awful service" -> negative
6. "It's okay" -> neutral
```

**After:**
```
- "Great product!" -> positive
- "Terrible service" -> negative
- "It's okay" -> neutral
```

Keep examples that pin a format the caller parses; drop examples of judgment the model already makes well.

### 4. Reference material

- Inlined on every call and read by most calls: keep it, inside the cached prefix.
- Inlined on every call but read by few: move it behind retrieval or a tool.
- Images and PDFs: downscale to what the task needs; vision tokens scale with resolution.

### 5. Tool schemas

Tool definitions are billed on every request. Do not shorten descriptions to one-liners - an under-described tool causes wrong calls that cost more than the tokens saved. Instead load fewer tools per request (tool search or deferred loading), keep the list stable so it caches, and drop prose in the system prompt that restates the tool schemas.

### What not to do

- **Lossy token-dropping compressors** that delete "low-information" words produce text no author would write; current models follow instructions closely and literally, so mangled instructions are followed mangled. Prefer caching and removing whole redundant sections.
- **Invented abbreviations** (`usr=user, req=request`) save a few tokens and cost clarity on every request.
- **Shortening as a goal.** A shorter prompt is not automatically a cheaper task: the model may spend more turns or output tokens recovering context it used to have. Measure cost per completed task, not prompt length.

## Checklist

- [ ] Stable content before dynamic content; breakpoint at the boundary
- [ ] No timestamps, IDs, or per-user data in the stable section
- [ ] Deterministic serialization of tools and JSON
- [ ] Repeated instructions consolidated
- [ ] Filler phrasing removed; reasons and constraints kept
- [ ] Examples varied, not repeated
- [ ] Reference material cached or retrieved, not both
- [ ] Quality re-checked against the baseline (see quality-checklist.md)
