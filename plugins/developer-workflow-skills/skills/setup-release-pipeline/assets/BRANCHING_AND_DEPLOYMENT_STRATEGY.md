# Branching & Deployment Strategy

_Template — replace `<PROJECT>` and `<HOST>` placeholders. Remove sections that do not apply._

This document defines the branching strategy, PR flow, QA/QC stages, and production release process for `<PROJECT>`.

This workflow is simple but opinionated. Read the trade-offs before cutover; it is designed for small teams and agent-assisted projects that want host branch-tracking deploys without per-repo deploy secrets.

## 1. Summary

```text
feat/fix/docs/*
  → branch from develop
  → PR to develop
  → review & approval
  → merge to develop
  → development QA/QC
  → develop → main release PR
  → review & approval
  → merge to main
  → main now contains latest release-candidate code
  → ./run_deploy.sh <version>
  → production pointer fast-forwards to main HEAD
  → <HOST> production deployment
  → vX.Y.Z release tag pushed
```

Branch roles:

| Branch | Role | Deploy connection | Notes |
| --- | --- | --- | --- |
| `develop` | Development integration and QA/QC | Optional staging/preview/CI | Work branches merge here first. |
| `main` | Canonical latest-code / release-candidate branch | No production deploy after cutover | GitHub default branch. May be ahead of live production. |
| `production` | Live reflection branch / release pointer | <HOST> production deploy branch | Moved only by `run_deploy.sh`. Must be reachable from `main`. |
| `feat/*`, `fix/*`, `docs/*`, `chore/*` | Work branches | No direct deploy | Always branch from `develop`; PR back to `develop`. |

The key distinction:

```text
main = latest code / release candidate
production = what users actually see
```

## 2. Why this strategy

Many hosting platforms make this easy:

```text
watched branch push → production deploy
```

If the watched branch is `main`, every merge to `main` ships immediately. That is often too aggressive, especially when `main` is also the branch the user wants to show as the latest code HEAD.

Instead, configure the host to watch `production`. Then `main` can keep moving as the release-candidate branch, and production only changes when `run_deploy.sh` explicitly advances the `production` pointer.

Benefits:

- Avoids GitHub Actions / Vercel CLI / provider secrets setup.
- Works well with agents that cannot configure secrets in GitHub or Vercel.
- Keeps `main` as the canonical latest-code branch.
- Makes release a deliberate action rather than a side effect of merging.
- Uses the host's native branch deployment model instead of custom CD plumbing.

Trade-offs:

- `main` may be ahead of live production.
- `production` must be treated as a pointer, not a working branch.
- The team must understand that production deploy is triggered by moving `production`, not by pushing tags.
- Preview builds for `main` may still happen depending on host settings.

## 3. `develop` branch — development and QA/QC

`develop` is the integration branch for day-to-day work.

Purposes:

- collect feature/fix/docs changes;
- run local and development-stage QA/QC;
- run staging/preview deployment if configured;
- prepare changes before promotion to `main`.

All normal work branches are based on `develop` and PR back into `develop`.

## 4. Work branch rules

All work branches should be created from up-to-date `develop`.

```bash
git switch develop
git pull --ff-only origin develop
git switch -c feat/my-change
```

Naming:

| Prefix | Use case | Example |
| --- | --- | --- |
| `feat/` | New feature | `feat/add-provider-section` |
| `fix/` | Bug fix | `fix/mobile-cta-layout` |
| `docs/` | Documentation | `docs/update-deployment-guide` |
| `chore/` | Config/build/dependency/maintenance | `chore/update-release-pipeline` |
| `refactor/` | Structure change without behavior change | `refactor/split-hero-section` |
| `test/` | Tests | `test/add-release-flow-tests` |

PR rule:

```text
base: develop
head: feat/my-change
```

Before merge:

- purpose is clear;
- local tests/build pass where available;
- UI/UX and accessibility are not regressed;
- reviewer approves.

## 5. `main` branch — latest code / release candidate

`main` is the GitHub default branch and the canonical latest-code branch. It is where release candidates live.

Important:

> `main` is not guaranteed to equal live production after cutover.

Promotion into `main` normally happens through a release PR:

```text
base: main
head: develop
```

Use this PR to review the exact scope being promoted toward production.

Release PR checklist:

- `develop` QA/QC is complete;
- diff scope is intentional;
- reviewer approves;
- release version is decided;
- rollback/hotfix implications are understood.

Merging into `main` still does not ship to users. Shipping happens only when `production` is advanced.

## 6. `production` branch — live reflection pointer

`production` is the host's Production Branch. It is what users see.

It is not a normal branch for development or code review. During normal releases, it is a pointer moved by `run_deploy.sh`.

Invariant:

```text
Every commit on production must already exist on main. Immediately after release, production may equal main.
```

This prevents a release from dropping commits. `run_deploy.sh` checks that `origin/production` is an ancestor of `origin/main` before moving it.

Do not:

- branch feature work from `production`;
- open normal PRs into `production`;
- manually commit to `production`;
- treat `production` as the repo default branch.

## 7. Production release flow

From local `main`:

```bash
git switch main
git pull --ff-only origin main

./run_deploy.sh          # inspect previous releases + suggested next patch
./run_deploy.sh 0.1.0    # release
```

The script verifies:

- current branch is `main`;
- working tree is clean;
- local `main` equals `origin/main`;
- `origin/production` is reachable from `origin/main`;
- version format is `x.y.z`;
- tag does not already exist.

After confirmation, it:

1. moves `origin/production` to `origin/main` HEAD using `--force-with-lease`;
2. verifies the remote `production` branch now equals `origin/main`;
3. creates annotated tag `vX.Y.Z`;
4. pushes the tag to origin;
5. verifies the remote tag exists.

Before confirmation, it prints:

- pending commit count from `production` to `main`;
- oldest unreleased commit;
- commit list to ship;
- file diff summary for the release.

Deployment trigger:

```text
production branch move → <HOST> production deploy
```

The tag is release metadata unless the project separately configures tag-triggered automation.

## 8. Host configuration

In `<HOST>` dashboard, set the Production Branch / production deploy branch to:

```text
production
```

After cutover, verify the live deployment source/ref says `production`.

If `<HOST>` is Vercel, this is usually under project settings for Git / Environments / Production Branch, depending on the dashboard version and integration state.

## 9. GitHub default branch

Default branch should normally be:

```text
main
```

Reason:

- standard convention;
- shows the latest release-candidate code;
- avoids making the pointer-only `production` branch the repo homepage;
- keeps agent/developer work anchored around the canonical code branch.

Caveat:

- GitHub PRs may default to `main`; normal feature/fix/docs PRs should manually target `develop`.

## 10. Hotfix policy

Preferred hotfix path. This is the explicit exception to the normal "work branches start from `develop`" rule:

```text
fix/* from main
→ PR to main
→ review & approval
→ merge to main
→ ./run_deploy.sh <patch-version>
→ back-port / merge to develop
```

Emergency direct-to-production path:

```bash
git switch production
git pull --ff-only origin production
git cherry-pick <fix-commit-sha>
git push origin production
```

Only use this when there is truly no time for the preferred path. Immediately back-port the fix to `main` and `develop`; otherwise future releases can drop the hotfix.

## 11. Rollback

Rollback by rewinding `production` to a previous good tag.

```bash
git fetch origin --tags
git tag -l 'v*' --sort=-version:refname | head -5

GOOD_SHA="$(git rev-list -n 1 v0.1.2)"  # replace with last good tag

# Safety: rollback target must still be part of main history.
git merge-base --is-ancestor "$GOOD_SHA" origin/main

git push --force-with-lease origin "$GOOD_SHA":refs/heads/production
```

`<HOST>` redeploys from the rewound `production` pointer. `main` remains unchanged for investigation.

## 12. Operational checks and optional verification

Check main-production divergence at any time:

```bash
scripts/check_release_status.sh
```

Useful thresholds:

```bash
MAX_COMMITS=10 MAX_DAYS=7 scripts/check_release_status.sh
```

Optional secret-free GitHub Actions workflow:

```text
.github/workflows/verify-production-pointer.yml
```

This workflow does not deploy. It verifies that `origin/production` is reachable from `origin/main` and prints pending commits. It can run on PRs to `main`, pushes to `main`/`production`, and manual dispatch.

Recommended release PR template:

```text
.github/pull_request_template.md
```

Use the template to document release scope, QA/QC, risk level, target version, and rollback plan.

## 13. Checklists

### Before opening a feature/fix/docs PR

- [ ] Branched from up-to-date `develop`.
- [ ] Branch name uses the correct prefix.
- [ ] Local checks/build pass where available.
- [ ] PR base is `develop`.

### Before opening a release PR

- [ ] `develop` QA/QC complete.
- [ ] Release scope understood.
- [ ] Reviewer assigned/approved.
- [ ] Release version chosen.

### Before shipping production

- [ ] Host Production Branch is `production`.
- [ ] Local branch is `main`.
- [ ] `main` is up to date with `origin/main`.
- [ ] Working tree is clean.
- [ ] `./run_deploy.sh <version>` completed.
- [ ] Host production deployment succeeded.
- [ ] Production URL spot-check passed.

## 14. Common commands

Start work:

```bash
git switch develop
git pull --ff-only origin develop
git switch -c feat/my-change
```

Prepare release:

```bash
git switch develop
git pull --ff-only origin develop
# open develop → main PR
```

Ship release:

```bash
git switch main
git pull --ff-only origin main
./run_deploy.sh 0.1.0
```

Inspect releases:

```bash
git fetch origin --tags
git tag -l 'v*' --sort=-version:refname | head
```
