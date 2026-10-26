---
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---
Please add pytest unit tests for `slugify()` in `src/utils/text.py`. It's a pure function: it lowercases, strips accents, and collapses any run of non-alphanumeric characters into a single hyphen. Cover empty strings, leading and trailing punctuation, and non-Latin input.
