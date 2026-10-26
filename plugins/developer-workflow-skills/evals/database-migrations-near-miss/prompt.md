---
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Everything for this release is already merged into main. Before I advance production, can you go through what changed between the v1.8.0 tag and main and tell me what is risky to deploy: dropped tables or columns, new env vars we may not have set, breaking API changes, and anything we couldn't roll back by reverting?
