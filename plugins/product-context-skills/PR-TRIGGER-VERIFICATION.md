# PR automation 0.3.0 verification

This corrects the omitted PR trigger in 0.2.0. A user-enabled repository workflow
is standing authorization for its bounded documentation update. Codex-authored
PRs and Claude-authored PRs use the same Claude subscription OAuth writer.

## Authentication and execution choice

The official Claude Code Action accepts `claude_code_oauth_token`; its setup guide
directs Pro/Max users to `claude setup-token`:
https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md

Codex's official non-interactive guide supports saved CLI login locally, but
explicitly excludes the described ChatGPT-managed CI authentication workflow from
public/open-source repositories:
https://learn.chatgpt.com/docs/non-interactive-mode

This implementation keeps local Claude/Codex MCP support and uses only the
official Claude Action for hosted PR automation. No model API key/fallback is
configured. GitHub runner allowances, Claude account limits and any account
extra-usage settings still apply. Login checks are not billing/entitlement proof.

## Reproducible checks

Public Python CLI tests use temporary Git repositories, real Git worktrees,
the actual context collector, real guarded receipt computation and synthetic
filesystem verifier inputs. No project-owned module is mocked. They exercise
workflow emission, read-only planning, existing workflow preservation, trusted PR
gates, current-snapshot skip, source/decision changes, head races, completion and
scope gates, ignored outputs and published receipt persistence in a fresh clone.

Real MCP tests use the pinned OpenWiki backend and actual stdio protocol. External
CLI authentication is faked. A new test proves official subscription `oauth_token`
authentication can complete generation, and another confines CI MCP calls to the
configured product repository. Both new behaviors were observed failing before
their fixes. No model/provider is called by these tests.

Validation commands and results are recorded in the implementation ledger and
the follow-up PR. Public PR CLI suite: **16 passed**. Full repository command
`uv run --no-project --with pytest python -m pytest --import-mode=importlib -q`:
**140 passed, 10 subtests passed**. Real MCP suite: **18 passed**.
`actionlint` v1.7.7 validates the actual emitted workflow data,
including GitHub expression contexts; no shellcheck/pyflakes integration was used.
Canonical/distribution bundles are compared byte-for-byte. Runtime dependencies
are unchanged from 0.2.0, with exact pins and dependency lifecycle scripts disabled.

## One independent review and one fix pass

Four material integration issues were reproduced as failing public contracts:

1. The official Action expects a Git repository at the workspace root. The
   product now occupies that location, while the pinned harness is fetched into
   the runner's temp directory.
2. The Action restores protected configuration from the base branch. Generation
   and publication now use a separate detached evidence worktree preserving the
   exact PR head, while keeping the Action's restoration behavior intact.
3. Agent mode rejects bots unless explicitly allowed. Workflow and preflight now
   share a narrow GitHub Actions/Claude/Codex connector bot allowlist; unknown bot
   actors and external forks are rejected.
4. Ignored new pages/receipts could pass working-tree verification without being
   committed. Preflight and publication now reject ignored required outputs;
   the index must include required receipts before committing. A fresh-clone
   regression verifies current status survives a normal publication.

The review's path-filter wording concern is documented accurately: filters use
the accumulated PR diff, so a documentation-only push can still invoke preflight;
unchanged context then skips the model. No second model reviewer was run.

## Activation boundary

The `CLAUDE_CODE_OAUTH_TOKEN` repository secret was absent during implementation.
No token was read from local credential storage, copied to GitHub, or printed.
No hosted Claude generation/push was claimed or performed without that secret.
The checked-in workflow reports the missing prerequisite explicitly when a
changed source snapshot needs generation; it has no API fallback.

The completed code and emitted workflow can be reviewed before credentials are
configured. Set the secret through GitHub's secret UI or the interactive GitHub
CLI, then observe an eligible PR run to verify OAuth delivery, provider acceptance
and actual publication. Branch protection/organization policies may reject the
normal push; this is reported as failure and never bypassed with a force push.

## Review rulings and limitations

- Hosted execution, OAuth delivery/expiry, entitlement, quota and billing require
  the user's configured secret and a live run. Local tests cannot prove them;
  the risk is a failed run or account allowance consumption.
- Semantic wiki accuracy and whether sixteen turns suffice require inspecting a
  generated result. The bounded run may stop incomplete and will not be published.
- The user's actual Codex GitHub identity was not observed. Human-authored PRs and
  the listed connector bot are supported; another identity needs explicit policy
  configuration or it will be rejected.
- Repository branch protection, Actions policy and push authorization were not
  independently changed or verified; they can block publication.
- This is not a full dependency/source security audit or a sandbox against a
  malicious trusted collaborator who can change workflows; that threat remains.
- The reviewer did not independently rerun the suites or authenticate to local
  accounts. The author ran the complete suites and separately verifies local
  registration; supplied results are not an independent execution claim.
- Fix effectiveness is established by RED→GREEN reproductions and whole-suite
  reruns, rather than a second reviewer or unperformed hosted generation test.
