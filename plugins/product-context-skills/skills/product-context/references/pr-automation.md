# PR-triggered wiki updates

PR events drive automation. Claude Code or Codex can author the code and source
specs; one Claude subscription-authenticated GitHub Actions job maintains the wiki.
No interactive session needs to remain open and no model API key is configured.

## One-time opt-in per product

Prefer the integrated [product setup and doctor](product-setup.md). It reports
local installation, this product's cloud configuration, and real PR publication
separately, and makes the OAuth stage visible as incomplete until it is configured.
The lower-level workflow installer below reports `completion: workflow_only`;
it is not an operational PR automation verdict.

1. Initialize and review `.product-context.json` using the offline CLI. Select the
   actual specs, decision history and implementation evidence. The default init
   profile selects documents; add implementation paths when code-only PRs should
   refresh the wiki. Generated `openwiki/**` must stay outside primary sources.
2. Select a reviewed full commit SHA of `dabsdamoon/my-little-skills` containing
   this runtime version, then generate the workflow relative to this skill:

   ```sh
   python3 scripts/pr_wiki.py install --repo /path/to/product --runtime-ref REVIEWED_40_CHARACTER_SHA
   python3 scripts/pr_wiki.py install --repo /path/to/product --runtime-ref REVIEWED_40_CHARACTER_SHA --write
   ```

   The first command is read-only. The second creates
   `.github/workflows/product-context-wiki.yml`; it preserves a different existing
   workflow. The generated file uses JSON syntax, which is valid YAML, so it can
   be inspected without an extra YAML dependency. Commit the source profile and
   workflow in the product repository. Each product owns its source selection.
3. Run `claude setup-token` interactively with the subscribed Claude account.
   Store its generated value in that repository's Actions secret named
   `CLAUDE_CODE_OAUTH_TOKEN`. Use GitHub Settings → Secrets and variables → Actions,
   or `gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo OWNER/REPO`. Do not paste the
   token into chat, source files, workflow text or logs. The workflow uses the
   built-in GitHub token; installing the Claude GitHub app is not required for
   this configuration.

Both the harness and third-party Actions are pinned to full commit SHAs. Updating
the central skill does not silently update a product's pin; review and regenerate
the product workflow when upgrading. Branch protection must allow the generated
documentation commit; a rejected push is reported as failure, never force-pushed.

## Automatic execution

`opened`, `synchronize`, `reopened` and `ready_for_review` PR events are supported.
Same-repository, non-draft PRs by an owner/member/collaborator or the explicitly
listed GitHub Actions, Claude and Codex connector bots are eligible. Unknown bot
actors and external forks do not receive a credential-bearing run. The official
Action receives the same explicit bot allowlist. Review these identities when
adapting the workflow to other automation accounts.

Generated-only PR diffs are excluded by the path filter; decision changes remain
inputs. Path filters inspect a PR's accumulated diff, so a documentation-only push
to a PR that also changes sources can still run preflight. The current-snapshot
check then skips model execution. Publishing with the built-in GitHub token also
avoids recursively triggering ordinary push/PR workflows.

The trusted harness validates the exact triggering head and runs the real offline
context collector plus wiki receipt check before invoking a model. A current
source snapshot and current wiki skip the writer. Missing sources, broken links,
or a self-referential source profile fail before model execution.
Required wiki/review outputs must be trackable by Git. Ignore rules that exclude
new receipts or wiki artifacts fail explicitly; the workflow never force-adds
arbitrary ignored files.

The Action's workspace contains the checked-out PR Git repository. The trusted
harness and a separate detached evidence worktree live under the runner's temp
directory. The official Action can restore its own protected configuration from
the base branch without changing the source evidence used for generation or
publication. No PR hook or build script is executed to create this evidence copy.

When needed, the official Claude Code Action starts a new job using the
subscription OAuth token, the three-page MCP budget and at most sixteen Claude
turns. It reads the primary sources, updates the wiki, finishes cleanly and
records the inspected snapshot and unresolved questions. Missing OAuth fails
explicitly; no API-key or second-model fallback is present. Local MCP maintenance
still supports either Claude Code or Codex.

The writer receives the OAuth secret as `PRODUCT_CONTEXT_SESSION`; the generated
MCP config assigns its `${PRODUCT_CONTEXT_SESSION}` reference to the child's
`CLAUDE_CODE_OAUTH_TOKEN`. Only the reference is stored. Referencing the reserved
credential name itself did not deliver it in the pinned native CLI, as reproduced
with a synthetic token and no model call. A subscription-authenticated parent
does not by itself establish authentication in a restricted MCP child process.

The workflow emits selected MCP connection/tool-call metadata, known MCP error codes
and completion status after the writer. It does not print prompts, tool arguments,
tool results, credentials or the model's final text. Full transcript logging stays
disabled; an Action step reporting success still has to pass the receipt verifier.

Before publication, the verifier requires current wiki/review receipts, preserved
primary evidence and decision history, and confined document outputs. Existing
agent instructions may change only inside the OpenWiki-managed block; existing
ignore rules remain intact. Incomplete runs or unrelated edits fail. A normal
Git push publishes the verified documentation to the same PR branch. A newer
remote head rejects a stale push instead of overwriting newer work.

Subscription quotas, extra-usage settings and GitHub Actions runner allowances
remain applicable. The page/turn bounds limit work, not a guaranteed token count.
The login check establishes the reported authentication method, not entitlement
or billing verification. A completed receipt is not semantic product approval.

## Diagnostics

`prepare --repo ROOT --event EVENT_JSON --state OUTSIDE_REPO_JSON` performs the
model-free preflight and writes a trusted state record and bounded MCP settings.
`verify --repo ROOT --state STATE_JSON` verifies a completed run without publishing;
`--commit` creates the local documentation commit. The workflow performs the final
normal push with the built-in repository token after verification succeeds.

If the OAuth secret is missing, the workflow is installed but not operational.
Do not claim end-to-end cloud generation was verified from a local test or from
successfully generating the workflow alone.

Version 0.4.0 uploads a bounded `product-context-publication-NUMBER` artifact only
after the verified documentation push succeeds. It contains source/published
commits, the inspected snapshot and receipt hashes, never credentials or model
transcripts. Use `product_setup.py doctor --repo ROOT --pr NUMBER` to validate this
evidence against the current PR head. A skipped writer does not create new proof.
