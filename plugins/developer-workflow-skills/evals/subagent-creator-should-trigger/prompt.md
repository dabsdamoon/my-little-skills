---
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---
I want a reviewer agent for this repo that I can hand my changes to when I'm done with a feature. It should only read code, look at the git diff, and run the test suite. It must never edit files. Can you set that up?
