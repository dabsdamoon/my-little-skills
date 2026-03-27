# my-little-skills

A curated Claude Code plugin marketplace that bundles [Anthropic's official skills](https://github.com/anthropics/skills) with custom-built skills for developer workflows, document processing, design, and project-specific automation.

## Quick Start

Register this marketplace in Claude Code:
```
/plugin marketplace add dabsdamoon/my-little-skills
```

Browse and install plugins:
```
/plugin
```
Then go to the **Discover** tab, or install directly:
```
/plugin install <plugin-name>@my-little-skills
```

## Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| **document-skills** | xlsx, docx, pptx, pdf | Create, read, edit spreadsheets, Word docs, presentations, and PDFs |
| **design-skills** | frontend-design, algorithmic-art, canvas-design, brand-guidelines, theme-factory, slack-gif-creator, web-artifacts-builder | Frontend UI, generative art, visual design, and brand styling |
| **developer-workflow-skills** | pr-creator, webapp-testing, docker-ram-checker, mcp-builder, prompt-optimizer, subagent-creator, debugging-retrospective, gcloud-direnv-setup | PR docs with blast radius & security analysis, Playwright browser testing, Docker memory checks, debugging postmortems, and more |
| **writing-skills** | doc-coauthoring, internal-comms, skill-creator, system-prompt-creator | Documentation workflows, internal comms, skill/prompt authoring |
| **resume-skills** | resume-formatter, resume-translator, resume-project-summary | Resume formatting, EN/JP/KR/CN translation, portfolio summaries from codebases |
| **config-skills** | claude-config-migrator, update-notes, update-houmy-notes | Migrate Claude Code config between repos, write update notes |
| **houmy-skills** | houmlike-design, houm-refactoring | Houmy maternity care service: branded UI design and systematic codebase refactoring |
| **claude-api** | claude-api | Claude API & SDK reference across Python, TypeScript, Go, Java, PHP, Ruby, C#, curl |
| **translation-skills** | translate-book | Translate entire books (PDF/DOCX/EPUB) into any language using parallel sub-agents |

## What's Included from Upstream

This marketplace tracks [anthropics/skills](https://github.com/anthropics/skills) as an upstream remote. The following skills come directly from Anthropic's official repository:

algorithmic-art, brand-guidelines, canvas-design, claude-api, doc-coauthoring, docx, frontend-design, internal-comms, mcp-builder, pdf, pptx, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing, xlsx

To sync with upstream:
```bash
git fetch upstream
git rebase upstream/main
```

## Custom Skills

These skills are original to this marketplace — not available in Anthropic's official repo.

### Developer Workflow

| Skill | What It Does |
|-------|-------------|
| **pr-creator** | Generates PR documentation with blast radius analysis (how many files depend on your changes) and OWASP security scanning of the diff |
| **docker-ram-checker** | Tests Docker container memory usage before deploying to Cloud Run, ECS, or Kubernetes |
| **prompt-optimizer** | Reduces token usage and improves cache efficiency for production LLM prompts |
| **subagent-creator** | Generates repository-specific Claude Code subagents tailored to your tech stack |
| **debugging-retrospective** | Summarizes debugging sessions into educational postmortems with lessons learned |
| **gcloud-direnv-setup** | Configures per-directory GCP credentials with direnv for multi-account setups |

### Translation

| Skill | What It Does |
|-------|-------------|
| **translate-book** | Translates entire books (PDF/DOCX/EPUB) into any language using 8 parallel sub-agents with SHA-256 manifest validation. Outputs HTML, DOCX, EPUB, PDF. Requires Calibre + Pandoc. ([source: deusyu/translate-book](https://github.com/deusyu/translate-book)) |

### Resume & Career (Work in Progress)

> These skills are still being curated and may not work reliably yet.

| Skill | What It Does |
|-------|-------------|
| **resume-formatter** | Reformats resumes to match specific company templates while preserving content |
| **resume-translator** | Translates resumes between English and Japanese, Korean, or Chinese (.docx) |
| **resume-project-summary** | Generates portfolio-ready project summaries from codebases for resumes |

### Configuration & Ops

| Skill | What It Does |
|-------|-------------|
| **claude-config-migrator** | Transfers Claude Code config (rules, skills, hooks, MCP) between repositories |
| **system-prompt-creator** | Guides creation of production system prompts following OpenAI, Anthropic, Google, and OWASP best practices |
| **update-notes** | Writes concise release/update notes for projects |

### Houmy (Project-Specific)

| Skill | What It Does |
|-------|-------------|
| **houmlike-design** | Branded UI design for Houmy, a maternity care service — applies Houm's design philosophy to web interfaces |
| **houm-refactoring** | Systematic refactoring for Houmy's Python/FastAPI + React/Vite codebase — replaces implicit/magic patterns with explicit, grep-able code |
| **update-houmy-notes** | Writes update notes specific to the Houmy repository |

## Repository Structure

```
.claude-plugin/
  marketplace.json          # Marketplace registry
plugins/
  document-skills/          # Plugin: .claude-plugin/plugin.json + skills/
  design-skills/
  developer-workflow-skills/
  writing-skills/
  resume-skills/
  config-skills/
  houmy-skills/
skills/                     # Source skills (copied into plugins)
spec/                       # Agent Skills specification
template/                   # Skill template for creating new skills
```

## Creating a New Skill

Each skill is a folder with a `SKILL.md`:

```markdown
---
name: my-skill
description: "When and how to trigger this skill"
---

# Instructions for Claude here...
```

To bundle skills into a plugin, create a `plugins/<name>/.claude-plugin/plugin.json` and add the entry to `marketplace.json`. See any existing plugin for reference.

## Links

- [Agent Skills standard](https://agentskills.io)
- [Skills documentation](https://code.claude.com/docs/en/skills)
- [Plugins documentation](https://code.claude.com/docs/en/plugins)
- [Upstream: anthropics/skills](https://github.com/anthropics/skills)
