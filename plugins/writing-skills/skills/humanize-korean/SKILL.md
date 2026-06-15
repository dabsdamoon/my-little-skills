---
name: humanize-korean
description: AI(ChatGPT, Claude, Gemini 등)가 쓴 한국어 텍스트를 사람이 쓴 글처럼 윤문한다. Use when the user asks to remove Korean AI tells, humanize Korean, fix 번역투, remove ChatGPT/GPT tone, make Korean writing sound natural, or run Korean AI-style detection and rewriting. Works in both Claude Code and Codex: use Claude Code agents for strict verification when available, and otherwise use the portable fast path. Do not use for plain spellcheck, translation, or content expansion.
---

# Humanize Korean

Rewrite Korean text so it reads naturally while preserving meaning. Facts, claims, numbers, dates, names, quoted text, legal text, formulas, and technical abbreviations must remain unchanged.

## Runtime Choice

Use the best available path for the current environment:

1. **Claude Code strict path**: Use only when the user explicitly asks for `--strict`, "정밀 모드", "5인 파이프라인", or the input is over 8,000 Korean characters and Claude Code subagents are available.
2. **Claude Code fast path**: Use when Claude Code subagents are available and strict mode is not needed. Prefer the `humanize-monolith` subagent if installed.
3. **Portable fast path**: Use in Codex, or in Claude Code when subagents are unavailable. Do the detection, rewrite, and self-check directly from this skill and its `references/` files.

If a user requests strict mode in Codex or another runtime without subagents, say strict mode requires Claude Code agents, then continue with the portable fast path unless the user asks to stop.

## Inputs

Accept pasted Korean text or a `.txt`/`.md` file path. If the input is not Korean, stop and say that this skill only handles Korean text.

Options may appear naturally at the end:

- `장르: 칼럼|리포트|블로그|공적`
- `강도: 보수|기본|적극`
- `최소심각도: S1|S2|S3`
- `--strict`

Infer the genre from the first 300 characters when the user does not provide one.

## Required References

Always read `references/quick-rules.md` before rewriting. It is the slim runtime rulebook.

Read the larger references only when needed:

- `references/ai-tell-taxonomy.md`: full A-J pattern taxonomy and severity details.
- `references/rewriting-playbook.md`: category-specific rewrite recipes and genre allowances.
- `references/scholarship.md`: academic anchors for translationese patterns.
- `references/web-service-spec.md`: only for web-service expansion requests.

## Output Location

Create output under the current working directory:

```text
_workspace/YYYY-MM-DD-NNN/
  01_input.txt
  final.md
```

Use the current local date. Pick the next `NNN` by checking existing `_workspace/YYYY-MM-DD-*/01_input.txt` or `final.md` folders. Preserve the original input in `01_input.txt`.

## Portable Fast Path

Use this path in Codex and whenever agents are unavailable.

1. Load `references/quick-rules.md`.
2. Save the input as `_workspace/{run_id}/01_input.txt`.
3. Detect A-J AI-tell patterns from the quick rules. Exclude Do-NOT spans: proper nouns, numbers, dates, direct quotes, legal provisions, formulas, and standard abbreviations such as LLM, GPU, API, and MCP.
4. Rewrite only detected spans. Do not edit unsupported areas.
5. Apply fixes in this order: D 관용구 삭제, A 번역투, I 형식명사, G hedging, H 접속사, F 수식/중복, B 영어 인용, C/J 구조와 장식, E 리듬.
6. Preserve register. Formal input stays formal; casual input stays casual.
7. Track change rate. Warn above 30%; stop and roll back above 50%.
8. Self-check the result with the six quick-rules checks. If a check fails, roll back the offending edit and retry that local span once.
9. Write `_workspace/{run_id}/final.md`.

At the end of `final.md`, add one HTML comment block:

```html
<!-- HUMANIZE-SUMMARY
original_chars: ...
rewritten_chars: ...
change_rate: ...%
detected_before_after: ...
self_check: N/6
grade: A|B|C|D - one-line reason
highlights:
- before -> after
-->
```

Reply briefly with:

- Status line: `완료. 변경률 X% / 등급 Y / 자체검증 N/6 통과`
- Four to six key detections or category counts.
- One representative before -> after highlight.
- The path to `final.md`.

Do not paste the full rewritten text in chat unless the user explicitly asks.

## Claude Code Fast Path

When the `humanize-monolith` subagent is available, call it once with:

```text
input_path: <cwd>/_workspace/{run_id}/01_input.txt
quick_rules_path: <this skill directory>/references/quick-rules.md
genre_hint: 칼럼 | 리포트 | 블로그 | 공적 | null
```

The subagent should write `final.md` and its summary metadata. If the subagent is unavailable or fails, fall back to the portable fast path.

## Claude Code Strict Path

Use only in Claude Code with the bundled subagents installed.

Pipeline:

1. `ai-tell-detector` -> `_workspace/{run_id}/02_detection.json`
2. `korean-style-rewriter` -> `03_rewrite.md` and `03_rewrite_diff.json`
3. Run verification in parallel:
   - `content-fidelity-auditor` -> `04_fidelity_audit.json`
   - `naturalness-reviewer` -> `05_naturalness_review.json`
4. Accept, rewrite round 2, rollback and rewrite, or hold for human review based on the verification results.
5. Write `final.md` and the same `HUMANIZE-SUMMARY` block used by the fast path.

Maximum rewrite rounds: 3.

## Quality Bar

- **A**: S1 0, S2 2 or fewer, change rate 10-25%, self-check 6/6.
- **B**: S1 0, S2 4 or fewer, self-check at least 5/6.
- **C**: S1 remains, S2 exceeds the B threshold, or over-polish signals appear.
- **D**: meaning risk, severe over-polish, or unresolved S1 clusters.

For C/D in Codex, recommend rerunning in Claude Code strict mode.
