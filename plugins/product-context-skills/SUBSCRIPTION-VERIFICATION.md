# Subscription runtime 0.2.0 verification

Verified on macOS on 2026-11-16 against OpenWiki 0.9.0, MCP SDK 1.32.1 and Zod
4.6.7. Dependency versions and integrity records are pinned in the runtime npm
lockfile. Dependency lifecycle scripts are disabled during explicit setup.

## Real protocol and filesystem contracts

`node --test skills/product-context/tests/subscription-wiki.test.mjs`:
**15 passed**. Each generation test uses actual MCP client/server transport,
the real OpenWiki backend, a temporary Git product, persisted pages and Claims.
Only external host-login CLI responses are faked in these tests; no project-owned
module or OpenWiki lifecycle is mocked. No model/provider is executed.

The new suite was first observed failing before the server existed. Additional
RED→GREEN regressions cover Codex status on stderr, resumed budget limits,
unsupported backend versions, non-first-party Claude providers and automatic
expansion of stale Claim pages.

Verified outcomes include:

- Init produces durable wiki pages and complete metadata without an API workflow.
- An existing wiki updates and keeps unchanged Claim IDs; a new MCP connection
  resumes an interrupted init with the original run ID and completed Claims.
- Source drift during generation blocks completion/recording; source or wiki-only
  drift after completion invalidates the receipt.
- Existing questions survive a subsequent explicit empty question array.
- API-authenticated/ambiguous hosts fail before product mutation. Existing custom
  workflows remain byte-for-byte unchanged; symlinked workflow paths are rejected.
- Direct, resumed and automatically expanded plans respect the page budget.

## Setup and repository regression checks

Public setup CLI tests cover a read-only plan, stable runtime installation,
idempotent registration for both hosts and preservation of an unowned MCP server.
These also failed before the setup script existed. The npm network boundary and
host configuration CLIs are faked in setup tests; the installed Node server and
its actual dependencies are loaded for its self-check.

Full Python repository suite:

```sh
uv run --no-project --with pytest python -m pytest --import-mode=importlib -q
```

Result: **102 passed, 10 subtests passed**. Plain pytest collection was first
attempted and reported same-name import collisions between the canonical and
distribution mirrors; importlib mode collects both bundles without weakening any
assertion. Both test bundles had runtime dependencies available; the distribution
copy used an ignored test-only symlink to the canonical dependency directory.
To reproduce in an independent checkout, run `npm ci --ignore-scripts` in each
bundle's runtime directory first.

Canonical/distribution content was compared byte-for-byte, excluding dependencies
and bytecode caches. Python syntax, JSON manifests/lockfile and `git diff --check`
were checked. The original 18 offline CLI contracts remain covered by the suite.

## Evidence boundaries

The earlier four-host experiment supplied baseline failures: accidental API
workflow generation, `sourceChanged` being reported as completion, re-init during
handoff and omitted structured questions. See the local evaluation report at
`/Users/dabsdamoon/projects/product-context-eval-20261116/README.md` when available.

This change does not claim semantic consistency, authenticated human approvals,
automatic extraction of prose questions or environment-aware policy replacement.
The server checks CLI login status; it is not an account billing controller or
receipt. Parent-agent reasoning and any fresh review consume their host usage.
No hooks, scheduled jobs, standalone model execution or API-key fallback are
installed by this integration.
