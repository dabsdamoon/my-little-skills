# Product Context Skills

Reusable, offline development tooling for evolving product decisions. This
plugin is independent of application language and does not require OpenWiki.

Install from the my-little-skills marketplace after this version is published:

```text
Claude Code: /plugin install product-context-skills@my-little-skills
Codex: codex plugin add product-context-skills@my-little-skills
```

The installation exposes `product-context`. Its bundled Python CLI is also
usable directly from this checkout; no dependency installation is needed.

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
the current agent to update documents still consumes that session's usage. CI can
call `check` without a model, but CI infrastructure can have its own costs.
No recurring workflow or automatic generation is installed by this plugin.

For a **read-only HoumDesk pilot**, use the example profile without adding files
to the product:

```sh
python3 skills/product-context/scripts/product_context.py check --repo /path/to/houmdesk --config skills/product-context/assets/houmdesk.json --json
```

Tests: `python3 -B -m unittest discover -s skills/product-context/tests -p 'test_*.py'`.
See the skill and its format reference for snapshots, decisions and exit codes.
