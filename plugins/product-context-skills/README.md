# Product Context Skills

Reusable product evidence and decision tooling with optional subscription-host
OpenWiki maintenance. The offline Python CLI needs no OpenWiki or model provider.

Install from the my-little-skills marketplace after version 0.3.1 is published:

```text
Claude Code: /plugin install product-context-skills@my-little-skills
Codex: codex plugin add product-context-skills@my-little-skills
```

The installation exposes `product-context`. Its bundled offline Python CLI is
also usable directly from this checkout without dependency installation.

```sh
python3 skills/product-context/scripts/product_context.py init --repo /path/to/product --product example
python3 skills/product-context/scripts/product_context.py check --repo /path/to/product --json
python3 skills/product-context/scripts/product_context.py prepare --repo /path/to/product
```

Those paths are relative to **this plugin directory**. In the marketplace source
checkout, `skills/product-context` at repository root is the canonical bundle;
the plugin's `skills/product-context` is its exact distribution mirror.

`init` writes local product configuration; `record` and `decision` explicitly
write product state. `check` and `prepare` are read-only. Evidence changes prompt
review, not automatic rejection of legitimate changes. Existing questions and
superseded decisions remain available to the next session.

The CLI contains no model/provider execution path. Reading this skill or asking
the current agent to update documents consumes that session's usage. CI can call
`check` without a model, but CI infrastructure can have its own costs.

For wiki generation, explicitly install the local MCP runtime once per machine:

```sh
python3 skills/product-context/scripts/setup_subscription_wiki.py --host both --json
python3 skills/product-context/scripts/setup_subscription_wiki.py --host both --install --json
```

The first command is a read-only plan. Setup requires Python 3.10+, Node.js
22.22+, npm and subscription logins for the selected hosts. It installs a pinned
OpenWiki 0.9.0 runtime with npm scripts disabled under
`~/.local/share/product-context/0.3.1`, then registers the user MCP server
`product_context` with Claude Code and Codex. Restart the hosts afterward.

The current subscribed agent writes the pages. The bridge calls no model,
checks CLI subscription authentication, prevents OpenWiki's default scheduled
API workflow, and bounds each generation plan to three pages by default. Existing
custom workflows are preserved and block generation. A clean completion receipt
checks source versions, wiki Markdown, Claims and metadata before the guarded
review tool can record the result. Existing wikis update and durable runs resume.
Local MCP setup installs no recurring generation or API-key fallback.

For PR-triggered updates using Claude subscription OAuth, see
[PR automation](skills/product-context/references/pr-automation.md). Codex-authored
PRs use the same workflow; the automatic writer uses Claude once per eligible
event. A tracked product-context profile, pinned workflow and repository secret
are required. Generating the workflow alone does not activate cloud generation.

See the skill's [subscription workflow](skills/product-context/references/subscription-wiki.md)
for setup, source-doc-first ordering, questions and failure handling. The existing
dotfiles baseline follows this marketplace for skill distribution; MCP setup is
an explicit per-machine step rather than a blanket `agent-sync` upgrade.

For a **read-only HoumDesk pilot**, use the example profile without adding files
to the product:

```sh
python3 skills/product-context/scripts/product_context.py check --repo /path/to/houmdesk --config skills/product-context/assets/houmdesk.json --json
```

Tests (run `npm ci --ignore-scripts` in `skills/product-context/runtime` first
when testing the optional bridge):

```sh
python3 -B -m unittest discover -s skills/product-context/tests -p 'test_*.py'
node --test skills/product-context/tests/subscription-wiki.test.mjs
```

See the skill and its format reference for snapshots, decisions and exit codes.
