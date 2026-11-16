# Subscription runtime 0.2.0 verification

Verified on macOS on 2026-11-16 against OpenWiki 0.9.0, MCP SDK 1.32.1 and Zod
4.6.7. Dependency versions and integrity records are pinned in the runtime npm
lockfile. Dependency lifecycle scripts are disabled during explicit setup.
`npm audit --omit=dev --json` reported zero known vulnerabilities in the installed
runtime on that date; this is a registry advisory check, not a source security audit.

## Real protocol and filesystem contracts

`node --test skills/product-context/tests/subscription-wiki.test.mjs`:
**16 passed**. Each generation test uses actual MCP client/server transport,
the real OpenWiki backend, a temporary Git product, persisted pages and Claims.
Only external host-login CLI responses are faked in these tests; no project-owned
module or OpenWiki lifecycle is mocked. No model/provider is executed.

The new suite was first observed failing before the server existed. Additional
RED→GREEN regressions cover Codex status on stderr, resumed budget limits,
unsupported backend versions, non-first-party Claude providers and automatic
expansion of stale Claim pages.
The final review also exposed premature finish releasing ownership while the
backend session remained usable. Its reproduction failed first; the fix retains
the lock after a recoverable finish failure and invalidates sessions on release.

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
- A premature finish preserves exclusive ownership while pending work continues.

## Setup and repository regression checks

Public setup CLI tests cover a read-only plan, stable runtime installation,
idempotent registration for both hosts, preservation of an unowned MCP server,
rejection of symlinked ancestors/registries and concurrent setup exclusion.
These also failed before the setup script existed. The npm network boundary and
host configuration CLIs are faked in setup tests; the installed Node server and
its actual dependencies are loaded for its self-check.
The two symlink cases and concurrent-install race were reproduced as failures
during the final review fix pass. All **six** setup contracts now pass. Setup
serializes npm and registration under a process-owned kernel lock and writes JSON
receipts atomically; a crashed installer releases its lock for an explicit retry.

Full Python repository suite:

```sh
uv run --no-project --with pytest python -m pytest --import-mode=importlib -q
```

Result: **108 passed, 10 subtests passed**. Plain pytest collection was first
attempted and reported same-name import collisions between the canonical and
distribution mirrors; importlib mode collects both bundles without weakening any
assertion. Both test bundles had runtime dependencies available; the distribution
copy used an ignored test-only symlink to the canonical dependency directory.
To reproduce in an independent checkout, run `npm ci --ignore-scripts` in each
bundle's runtime directory first.

Canonical/distribution content was compared byte-for-byte, excluding dependencies
and bytecode caches. Python syntax, JSON manifests/lockfile and `git diff --check`
were checked. The original 18 offline CLI contracts remain covered by the suite.

## Actual machine installation

The explicit setup command installed the real pinned npm runtime with scripts
disabled under `~/.local/share/product-context/0.2.0`. Both real CLIs registered
the user MCP server successfully. `claude mcp get product_context` reported
connected; `codex mcp get product_context --json` reported an enabled stdio server.
Actual MCP clients connected to the installed server for both hosts, discovered
13 tools and passed `product_context_subscription_status` with subscription
authentication, zero model calls, no provider execution and a three-page budget.
Repeating setup completed successfully without a duplicate registration.

The existing loose skills for both hosts were verified against the previous
baseline, backed up, and updated to the exact 16-file bundle. Runtime registration
uses the stable path rather than either worktree or plugin cache. The existing
dotfiles baseline already follows this marketplace; unrelated plugin updates
were not applied. Restart each host to load the new configuration and skill.

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

One fresh whole-branch review found the three material issues above; each received
a failing reproduction and passing fix, followed by the full suites. The review
declined to judge account entitlement/quota/billing, semantic correctness or human
approval, hostile concurrent filesystem replacement, and the security of every
transitive dependency. Those remain outside this verification. Its initial
uncertainty about live CLI registration/npm compatibility was resolved by the
actual installation and protocol probes described above. No additional model
review or paid generation experiment was run after that fix pass.
