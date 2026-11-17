# Product onboarding verification — 0.4.1

Scope: issue #57, distinguishing machine-local installation from a product's PR
automation configuration and an actual published wiki update. This report does
not infer production readiness from offline checks or another product's test.

## Local evidence

- Baseline: the existing 43 Python product-context tests pass after installing
  the already pinned runtime dependencies with npm scripts disabled.
- Regression: the old workflow installer had no explicit automation-readiness
  boundary. The new test requiring `workflow_only` and `automation_ready: false`
  fails before the change and passes afterward. Local setup similarly reports
  `local_only` rather than a product automation completion claim.
- Public CLI tests exercise real temporary Git products and real owned scripts.
  Only external GitHub/host/package-manager transport is faked. They cover missing
  profiles/workflows/OAuth, unavailable secret permissions, provided organization
  credentials, personal repository scope, reviewed source initialization,
  preserved custom workflows/secrets, explicit rotation, wrong-repository and
  unsafe-path refusal, ignored outputs, published configuration and runtime pins.
- Publication tests reject skipped writers, wrong PRs, stale published heads,
  changed receipt bytes, failed publication and missing artifacts. Exact supported
  base-branch exclusions are explicit; complex filters remain unknown.
- Review-driven regressions reproduce broken runtime dependencies being falsely
  ready, case-sensitive repository identity, and premature writes with ignored
  outputs. Each fails before its corresponding fix and passes after it.
- A real provider-style HTTP 401 diagnostic produces a distinct rejected OAuth
  state. Application text mentioning `authentication_error` plus a max-turn
  failure does not recommend replacing an otherwise unverified credential.
  Error transport containing a synthetic token is suppressed from CLI output.
- Full Python regression command (canonical tests; duplicate plugin mirrors
  excluded): `uv run --no-project --with pytest pytest -q skills/product-context/tests plugins/developer-workflow-skills/skills/dual-track-checklist-verifier/tests plugins/developer-workflow-skills/skills/webapp-testing/tests plugins/fde-estimation-skills/tests`
  — **132 passed, 17 subtests passed**.
- Existing real model-free MCP/OpenWiki lifecycle suite:
  `node --test skills/product-context/tests/subscription-wiki.test.mjs`
  — **18 passed**. These do not start a model or verify a cloud account's billing.
- The canonical skill and plugin distribution are byte-identical (24 files).
- A fresh read-only reviewer identified three Important defects and one partial
  write edge; the fixes have explicit regressions. The final narrow review closed
  the remaining authentication-classification finding. No cloud or credential
  operation was performed by the reviewer.

## Reference application check

Two bounded fresh-context read-only samples used the same scenario: local setup
reported both hosts registered, a harness test passed, but the product had no
profile, workflow or Actions OAuth. The baseline reference consumer correctly
reported missing product setup but found no unified readiness command. The revised
reference consumer located `product_setup.py doctor`, the integrated setup/OAuth
path and the three required completion rows. This demonstrates retrieval of the
new reference contract, not a general measured improvement in agent compliance.

## Actual product and cloud evidence

Before rollout, a read-only diagnosis of HoumDesk found both local subscription
logins available, but its profile, workflow and Actions OAuth missing. The proposed
0.4.0 managed runtime was not installed at that point. No credentials were read or
changed by diagnosis.

The first 0.4.0 harness run completed generation, guarded verification, publication
and artifact upload: [run 44059591900](https://github.com/dabsdamoon/my-little-skills/actions/runs/44059591900).
Doctor matched its exact published head and source snapshot; both local hosts
were subsequently installed and its three stages all passed.

The first real HoumDesk run authenticated, finished its one-page wiki and recorded
review, but the Action correctly rejected its reported 18 turns against the
16-turn limit. Nothing was published from that over-budget run. Ordinary CI also
reported the generated JSON-as-YAML workflow through Prettier. Version 0.4.1
supplies the trusted instructions and preflight evidence without duplicate model
reads, preserves final status/review and the same 16-turn bound, and respects the
existing formatter's generated-output exclusions. Both regressions have focused
tests, as does explicit migration from the exact 0.4.0 workflow.

Final bounded retry evidence and product rollout are recorded separately in
[the harness PR](https://github.com/dabsdamoon/my-little-skills/pull/58) and
[the HoumDesk setup PR](https://github.com/houm-ground/houm-desk/pull/125). A green
local suite or an earlier version's run is not a substitute for that evidence.
