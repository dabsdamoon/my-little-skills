---
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

I work for two clients on GCP, each with its own project and a different Google account. When I cd into ~/work/client-a I want gcloud and the Python client libraries to use client A's project and account, and client B's when I'm in ~/work/client-b. Their org blocks service account keys. What's the cleanest way to set this up on my Mac?
