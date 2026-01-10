---
name: debugging-retrospective
model: sonnet
description: Generate educational debugging retrospectives that summarize debugging sessions, analyze the problem-solving process, and extract lessons learned. Use when the user asks to summarize a debugging session, create a debugging postmortem, document what was learned from debugging, write a debugging retrospective, or analyze a debugging process for educational purposes.
---

# Debugging Retrospective

Generate structured retrospective documents from debugging sessions for educational purposes.

## Workflow

### Step 1: Gather Session Information

Before writing, collect key information from the current conversation:

1. **Initial Problem**: What issue triggered the debugging?
2. **Symptoms**: Observable behaviors, error messages, unexpected outputs
3. **Hypotheses Tested**: What was suspected and investigated?
4. **Dead Ends**: Approaches that didn't work and why
5. **Root Cause**: The actual source of the issue
6. **Solution**: What fixed it
7. **Verification**: How the fix was confirmed

If information is incomplete, ask the user to clarify missing details.

### Step 2: Write the Retrospective

Use the template structure from [references/template.md](references/template.md).

Key writing principles:
- Write for someone unfamiliar with the codebase
- Explain the "why" behind each debugging step
- Highlight decision points and reasoning
- Be honest about wrong turns - they're educational
- Focus on transferable patterns, not just this specific bug

### Step 2.5: Add "Explain Like You're 12" Sections

For complex technical concepts in **Root Cause** and **Lessons Learned** sections, add simplified explanations using everyday analogies. This makes the retrospective accessible to:
- Junior developers
- Non-technical stakeholders
- Future you who forgot the context

**How to write these sections:**

1. **Use physical world analogies**: Compare code concepts to cooking, buildings, traffic, mail delivery, etc.
2. **Avoid jargon**: Replace technical terms with simple descriptions
3. **Keep it relatable**: Use scenarios a 12-year-old would understand
4. **Explain the "why" behind the fix**: Not just what was done, but why it worked

**Example analogies:**
- Race condition → "Like two people trying to go through a door at the same time"
- Async state updates → "Like a chef showing you an incomplete sandwich before adding all ingredients"
- Cache issues → "Like getting yesterday's newspaper when you asked for today's"
- Missing conditional → "Forgot to add a rule that says 'only do this for certain people'"
- Environment mismatch → "Testing your cooking by eating at a restaurant instead"

### Step 3: Extract Lessons Learned

Derive actionable insights:

1. **Technical Lessons**: Language/framework-specific knowledge gained
2. **Debugging Strategies**: Effective approaches discovered
3. **Anti-patterns**: What to avoid in future debugging
4. **Process Improvements**: Changes to development workflow
5. **Knowledge Gaps**: Areas requiring further study

### Output Format

Default: Markdown document suitable for documentation or knowledge base.

Alternative formats on request:
- Concise summary (1-page)
- Detailed technical report
- Team presentation format
