# Product setup and completion

Local installation is shared across sessions on one machine. Source selection,
workflow publication and Actions subscription OAuth are configured per product.
All paths below are relative to this skill directory; pass the product Git root.
No setup/doctor command starts a model, and none reads existing login credentials.

## One product-aware entry point

```sh
python3 scripts/product_setup.py doctor --repo /product --github-repo OWNER/REPO --host both --json
python3 scripts/product_setup.py setup --repo /product --github-repo OWNER/REPO --host both --profile /reviewed/profile.json --runtime-ref REVIEWED_FULL_COMMIT_SHA --json
python3 scripts/product_setup.py setup --repo /product --github-repo OWNER/REPO --host both --profile /reviewed/profile.json --runtime-ref REVIEWED_FULL_COMMIT_SHA --write --json
```

The first command diagnoses without writes. The second is a read-only plan. The
third installs the managed runtime, registers selected hosts, initializes the
reviewed source profile, writes a pinned workflow and records the product opt-in
in `.product-context/automation.json`. Commit that record with the profile and
workflow. Profile contents use the existing [format](format.md). Include actual
implementation paths when code-only changes should affect the evidence snapshot.
The example HoumDesk profile is a starting point for review, not a blanket policy.

Existing profiles and secrets are preserved. A custom workflow is diagnosed as
unreviewed and is not replaced. A recognized generated workflow can be explicitly
migrated with `setup --upgrade-workflow` after reviewing the new runtime pin.
`--skip-local` is available for cloud-only setup; it does not mark local setup done.

When the product already has `.prettierignore`, setup preserves its rules and
adds only the generated workflow, `openwiki/` and `.product-context/` paths.
These generated artifacts retain their producer's formatting; product source
formatting remains governed by the existing rules.

## Required OAuth stage

If Actions OAuth is missing, setup stays incomplete and returns the next action.
The local host's subscription login is never used as proof of cloud credentials.
Run `claude setup-token` interactively with the subscribed account. Register the
newly issued token through hidden terminal input:

```sh
python3 scripts/product_setup.py oauth --repo /product --github-repo OWNER/REPO
```

This prompt hides input and sends the value directly to `gh secret set` through
stdin. For a trusted credential issuer already providing the newly issued token
on stdin, add `--token-stdin`. Never pass the token in argv, a temporary file, chat,
source, or logs. Do not pipe the complete interactive `claude setup-token` transcript
as though it were a raw token. No credential extraction or API-key fallback exists.

A noninteractive invocation without explicit stdin input returns
`INTERACTIVE_LOGIN_REQUIRED`; continue the interactive step in a terminal and
report setup as incomplete until it finishes. An existing repository or provided
organization secret is preserved. Unavailable secret-list permissions produce
`OAUTH_UNVERIFIABLE` and block blind replacement. Secret presence means configured,
not authenticated: validity is established by the actual bounded PR writer.

For an actual current-head writer failure, doctor can inspect bounded GitHub job
logs in memory and return the fixed `OAUTH_AUTHENTICATION_FAILED` code when the
provider explicitly reports rejected authentication. No log content is returned
or saved. This differs from missing OAuth and unavailable inspection permissions.
Issue a fresh subscription token and use `oauth --replace` for explicit rotation;
ordinary setup and `oauth` preserve existing credentials. Unknown failures remain
unverified instead of being guessed to be authentication failures.

## Required three-stage handoff

| Report row | Evidence | Insufficient evidence |
|---|---|---|
| Local installation | Correct managed runtime, host registration and subscription login | A skill folder or plugin name |
| Product PR configuration | Valid sources, reviewed pin/workflow, matching published config and provided Actions OAuth | A locally generated workflow or another repository's secret |
| Actual PR publication | Successful non-skipped writer/push, current PR head, run-bound artifact and matching wiki/review receipts | Ordinary CI success, skipped writer, local tests or offline `current` |

```sh
python3 scripts/product_setup.py doctor --repo /product --github-repo OWNER/REPO --pr NUMBER --json
```

With `--pr`, published configuration is inspected at the actual PR head and base
branch eligibility is reported. Without it, the repository default branch is
inspected; `--ref COMMIT_OR_REF` chooses another published configuration explicitly.
Exact base-branch filters are evaluated. Complex custom glob filters are reported
as unknown for review rather than approximated. Fork and draft exclusions are
explicit. Existing product authorization is reused; each session need not ask again.

The publication artifact is emitted only after successful receipt verification
and a normal push. Doctor verifies its repository, PR number, run, source head,
source snapshot, current published commit, known workflow and receipt bytes.
Artifacts expire after 30 days; expired/unavailable evidence is unverified, not a
new generation request. Existing older workflows lack the artifact and require
the explicit upgrade to provide this new verification contract.

Exit `0`: requested local/cloud configuration is ready (or OAuth is configured).
Exit `1`: incomplete or unknown readiness, with a usable diagnosis.
Exit `2`: invalid/unsafe input or a setup operation failed. All reports distinguish
`ready` configuration from `complete`, which additionally requires verified PR
publication. Do not relabel incomplete state as installed/operational.

Setup performs dependency installation and GitHub configuration requests only
when requested. Doctor uses read-only GitHub inspection and subscription-status
checks. Neither starts an LLM, background generation, a schedule, or an API fallback.
