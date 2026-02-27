# Quality Preservation Checklist

Ensure optimization does not degrade prompt effectiveness.

## Pre-Optimization Baseline

Before making changes, document current behavior:

### 1. Create Test Cases

Minimum 10 diverse inputs covering:

- [ ] Typical use cases (5-7 cases)
- [ ] Edge cases (2-3 cases)
- [ ] Error scenarios (1-2 cases)

**Test case template:**
```
ID: TC-001
Input: [user input]
Expected output: [expected response]
Quality criteria: [what makes this good]
```

### 2. Record Baseline Outputs

Run test cases with original prompt:

| Test ID | Input | Original Output | Quality Score |
|---------|-------|-----------------|---------------|
| TC-001 | ... | ... | 9/10 |
| TC-002 | ... | ... | 8/10 |

### 3. Note Edge Cases

Document known edge cases and how they're handled:

- Empty input: [behavior]
- Very long input: [behavior]
- Ambiguous queries: [behavior]
- Out-of-scope requests: [behavior]

---

## Post-Optimization Verification

### Semantic Equivalence Test

Run all test cases with optimized prompt:

| Test ID | Original Output | Optimized Output | Match? |
|---------|-----------------|------------------|--------|
| TC-001 | ... | ... | Yes/No |
| TC-002 | ... | ... | Yes/No |

**Pass criteria**: >95% semantic match

### Quality Metrics

| Metric | Original | Optimized | Delta |
|--------|----------|-----------|-------|
| Accuracy | % | % | |
| Format compliance | % | % | |
| Tone consistency | % | % | |
| Completeness | % | % | |

**Acceptable degradation**: <5% on any metric

### Edge Case Verification

Re-test all documented edge cases:

- [ ] Empty input: [still works]
- [ ] Very long input: [still works]
- [ ] Ambiguous queries: [still works]
- [ ] Out-of-scope requests: [still works]

---

## Quality Checks by Optimization Type

### After Token Compression

- [ ] No critical instructions removed
- [ ] Examples still representative
- [ ] Role definition intact
- [ ] Format requirements clear

### After Cache Restructuring

- [ ] Static/dynamic split logical
- [ ] No context dependencies broken
- [ ] Multi-turn conversations work
- [ ] Variable placeholders correct

### After Output Format Changes

- [ ] All required fields present
- [ ] Schema validates correctly
- [ ] Stop sequences don't truncate
- [ ] Max tokens sufficient

---

## A/B Comparison Guide

### Setup

1. Run both prompts on same inputs
2. Blind evaluation (don't know which is which)
3. Score each response

### Scoring Rubric

| Score | Criteria |
|-------|----------|
| 5 | Perfect - matches or exceeds original |
| 4 | Good - minor differences, acceptable |
| 3 | Acceptable - noticeable differences, still usable |
| 2 | Poor - significant degradation |
| 1 | Failed - unusable output |

### Decision Matrix

| Avg Score | Token Savings | Decision |
|-----------|---------------|----------|
| 4.5+ | Any | Accept |
| 4.0-4.4 | >30% | Accept |
| 4.0-4.4 | <30% | Review |
| 3.5-3.9 | >50% | Consider |
| <3.5 | Any | Reject |

---

## Rollback Criteria

Immediately revert if:

- [ ] Quality score drops >10%
- [ ] New failure modes appear
- [ ] Edge cases break
- [ ] User complaints increase
- [ ] Error rates increase

### Rollback Process

1. Document what went wrong
2. Revert to previous prompt
3. Analyze failure cause
4. Adjust optimization approach
5. Re-test before re-deploying

---

## Continuous Monitoring

After deployment:

### Metrics to Track

- Error rate (should not increase)
- User satisfaction (should not decrease)
- Task completion rate (should not decrease)
- Response latency (should decrease)
- Token usage (should decrease)

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error rate | +5% | +10% |
| Satisfaction | -5% | -10% |
| Completion rate | -5% | -10% |

---

## Quick Checklist

Pre-optimization:
- [ ] Test cases documented
- [ ] Baseline outputs recorded
- [ ] Edge cases noted

Post-optimization:
- [ ] Semantic equivalence verified
- [ ] Quality metrics within threshold
- [ ] Edge cases still work
- [ ] A/B comparison passed

Deployment:
- [ ] Monitoring in place
- [ ] Rollback plan ready
- [ ] Alert thresholds set
