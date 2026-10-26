---
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

I'm about to deploy my FastAPI image to Cloud Run with a 512Mi memory limit. How can I check locally how much RAM the container actually uses under load, so I know it won't get killed for running out of memory?
