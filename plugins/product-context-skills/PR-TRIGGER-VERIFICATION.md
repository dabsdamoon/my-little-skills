# PR automation 0.3.1 verification

PR events automatically maintain the product wiki through Claude subscription
OAuth, including PRs authored with Codex. Local Claude/Codex MCP support remains.
The workflow has no model API-key fallback or schedule.

## Hosted results

Actual same-repository PR #54 events completed generation, guarded verification
and normal publication to the PR branch:

| Case | GitHub run | Result |
| --- | --- | --- |
| Initial wiki | [43996653721](https://github.com/dabsdamoon/my-little-skills/actions/runs/43996653721) | Success; one quickstart, 13 turns, nine published paths; commit `4bd0339` |
| Primary README changed | [43997004332](https://github.com/dabsdamoon/my-little-skills/actions/runs/43997004332) | Success; existing page updated, 15 turns, six published paths; commit `635bb35` |

Both runs reported connected MCP, zero MCP errors and permission denials, and
current context/wiki receipts. Separate model-free checks after fetching the published
commits also reported both states current. The update retained the existing page
and Claim IDs, added the changed README evidence, and reflected setup version
0.3.1. These are live execution results, not just a rendered workflow or mocked
model response. The host model consumes the Claude account's allowance; helper
outputs of `model_calls: 0` describe the model-free helper itself.

## CI repairs

1. The OAuth secret was initially absent. The user completed official
   `claude setup-token` browser authorization, and the newly issued token was
   sent directly to repository secret `CLAUDE_CODE_OAUTH_TOKEN`. No credential
   value was printed or added to source.
2. A parent Claude login did not authenticate the MCP child. A model-free native
   Claude 2.1.325 probe reproduced failed forwarding of the reserved credential
   reference. The writer now explicitly receives `PRODUCT_CONTEXT_SESSION`, and
   MCP assigns `${PRODUCT_CONTEXT_SESSION}` to its `CLAUDE_CODE_OAUTH_TOKEN`.
   Generated configuration stores the reference only. The actual native CLI and
   SDK transport regressions failed before this change and passed afterward.
3. A credentialed run reached the sixteen-turn limit during page submission.
   The cap remains sixteen. New wikis start with one concise quickstart; an
   existing wiki may update up to three affected pages. A tested minimal protocol
   example supplies valid front matter, repository evidence URIs and exact job IDs.
4. Safe diagnostics report only selected MCP status, tool counts, error categories
   and completion metadata. Failed MCP results are correlated to their calls;
   error examples in a Read result cannot become false diagnostic errors.
   Prompts, arguments, result bodies, credentials and final model text stay hidden.

## Reproducible local validation

- Public PR CLI: **19 passed**. Tests use real temporary Git repositories,
  detached worktrees, the actual context collector and guarded verifier.
- Whole repository: `uv run --no-project --with pytest python -m pytest --import-mode=importlib -q`
  completed with **146 passed, 10 subtests passed**.
- `node --test skills/product-context/tests/subscription-wiki.test.mjs`:
  **18 passed**, using real stdio and pinned OpenWiki. External authentication
  fixtures use synthetic credentials; no model is called.
- The optional native Claude CLI boundary test starts an actual MCP under an
  isolated configuration with a synthetic token, without sending a model prompt.
- A model-free smoke probe completed actual OpenWiki planning, page/Claim
  submission, finish, review and verified documentation commit in a Git worktree.
- `actionlint` v1.7.7 passed the checked-in JSON/YAML workflow and expression
  contexts, with shellcheck/pyflakes integration disabled. `git diff --check`
  passed; canonical/distribution bundles have **19 identical files**.

Both local CLI registrations and loose skill bundles were upgraded to **0.3.1**
after verifying and backing up their previous managed contents. Each actual MCP
client discovered **13 tools**, advertised 0.3.1 and passed its subscription check.
The stable path is `~/.local/share/product-context/0.3.1`; no plugin-wide upgrade
or baseline policy change was performed. Restart hosts to load the new registration.

## Retained boundaries

The initial independent review identified and reproduced four integration issues:
Action workspace layout, protected-config restoration changing evidence, bot
allowlist mismatch, and ignored receipts not surviving publication. Each was
fixed with a failing-then-passing contract before this CI repair. No second model
review was used for the repair.

The workflow still uses a pinned harness outside the Action checkout and a
separate exact-head evidence worktree. It rejects external forks and unknown bots,
source/decision changes during generation, incomplete receipts and out-of-scope
outputs. Publication uses a normal push; branch policies are not bypassed.
Its accumulated PR path filter can run preflight after a documentation-only push;
unchanged selected evidence and current receipts skip the writer.

Observed success does not prove future OAuth expiry, entitlement or quota, every
organization policy, semantic correctness of all prose, or adequacy of sixteen
turns for every project. Current receipts mean matching evidence versions, not
product approval. This is not a full dependency audit or a sandbox against a
trusted collaborator who can modify workflows. Failed or unfinished work remains
unpublished.

Authentication uses the official [Claude Action setup](https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md).
The runtime variable reference follows the [MCP configuration mechanism](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json),
with native CLI behavior verified rather than assumed from the reference syntax.
