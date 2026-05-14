---
name: setup-release-pipeline
description: Use when a project deploys from a host-tracked branch such as Vercel, Netlify, or Render and the user wants `main` to remain the canonical latest-code/release-candidate branch while production ships only when a `production` pointer branch is explicitly advanced from `main` via `run_deploy.sh`. Best for reducing GitHub Actions/secrets setup, avoiding automatic live deploys on every merge to `main`, and giving agents a repeatable low-touch release workflow.
---

# Setup Release Pipeline (`production` pointer branch)

## Overview

This workflow is simple but opinionated. Read the trade-offs before cutover.

Use this skill to convert projects from:

```text
merge/push to main → host production deploys immediately
```

to:

```text
merge/push to main → latest code / release candidate only
./run_deploy.sh <version> → advance production pointer → host production deploys
```

The model is intentionally simple: keep the hosting provider's native branch-tracking deploy integration, but change the watched production branch from `main` to `production`. The `production` branch is not a normal development branch. It is a release pointer that should always point to a commit already reachable from `main`.

This avoids introducing GitHub Actions deploy workflows, Vercel CLI tokens, org/project IDs, and per-repo secrets that remote agents usually cannot configure for the user. Optional GitHub Actions in this skill are verification-only and require no secrets.

## Mental Model

| Branch | Role | Who touches it | Deploy behavior |
| --- | --- | --- | --- |
| `develop` | Development integration and QA/QC | feature/fix/docs PRs | Usually staging/preview or CI only |
| `main` | Canonical latest-code branch and release candidate | release PRs from `develop`; occasional hotfix PRs | **Not live by itself** after cutover |
| `production` | Live reflection branch / release pointer | `run_deploy.sh` during normal releases | Host production deploys when this branch moves |
| `feat/*`, `fix/*`, `docs/*`, `chore/*` | Work branches | agents/developers | No direct deploy |

Key rule:

> `production` must always point to a commit reachable from `main`. Immediately after release, `production` and `main` may point to the same commit.

If someone hotfixes `production` directly and forgets to back-port to `main`, the next regular release can drop that hotfix. The bundled script and optional CI workflow refuse to release/verify when they detect this condition.

## When to Use

Use this when:

- The user says merging to `main` currently deploys too quickly.
- The user wants `main` to show the latest code HEAD, but not necessarily the live state.
- The hosting provider already supports branch-tracking deployment.
- The user wants to avoid GitHub Actions/Vercel CLI/secrets setup for every small project.
- Agents will repeatedly set up deployment workflows and cannot reliably configure provider secrets.
- The desired release action is explicit: "ship the current `main` now".

When NOT to use:

- The project already has tag-driven GitHub Actions CD working and secrets management is not painful.
- The team/org requires `main == live production` as a strict GitOps rule.
- The team wants `production` to be a normal working branch.
- The host cannot watch a configurable production branch.
- The real problem is preview-build cost rather than live-deploy control. This strategy prevents live deploys from `main`, but the host may still create preview builds for `main` depending on provider settings.
- The project handles regulated environments where releases require formal change-control tooling beyond a branch pointer.

## Workflow

### Step 1: Gather context

Inspect before changing anything:

```bash
git fetch origin --prune --tags
git remote show origin | sed -n '/HEAD branch/s/^/  /p'
git branch -a --sort=-committerdate | head -40
git ls-remote --heads origin main develop production
find . -maxdepth 3 -type f \( -name 'vercel.json' -o -path './.github/workflows/*' -o -name 'netlify.toml' -o -name 'render.yaml' -o -name 'run_deploy.sh' \) | sort
```

Ask or infer:

1. Which host performs production deploys? Vercel / Netlify / Render / other?
2. Which branch is currently the host's Production Branch / deploy branch?
3. Does `develop` exist and serve as integration/QA?
4. Does `production` already exist?
5. Is `main` the desired GitHub default branch?
6. What production URL and host dashboard URL should the script print?

### Step 2: Explain and confirm the trade-off

Before touching deployment behavior, summarize the change:

```text
Current:  main → host production deploys immediately
Target:   main → release candidate only
          production → host production deploys
          ./run_deploy.sh <version> moves production to main HEAD

Gain: lower setup cost, no GitHub Actions deploy secrets, explicit release gate.
Cost: main may be ahead of live; production must never be manually developed.
```

Wait for explicit approval before editing files or asking the user to change the host dashboard.

### Step 3: Add or update `run_deploy.sh`

Copy `assets/run_deploy.sh` to the target repo root.

Replace placeholders:

- `{{PROJECT_URL}}` → production URL, e.g. `https://example.vercel.app`
- `{{HOST_DASHBOARD_URL}}` → deployment dashboard URL if known

Then:

```bash
chmod +x run_deploy.sh
bash -n run_deploy.sh
```

The script should enforce/show:

| Check / output | Why |
| --- | --- |
| current branch is `main` | Releases are cut from canonical latest code |
| working tree is clean | Avoid shipping uncommitted local state |
| local `main` equals `origin/main` | Release what collaborators can see |
| `origin/production` is reachable from `origin/main` | Protect the live-pointer invariant |
| pending release count and oldest pending commit | Make main-production divergence visible |
| release diff summary (`production..main`) | Make the release scope reviewable before shipping |
| version is `x.y.z` | Keep release tags predictable |
| local and remote tag do not already exist | Avoid clobbering release history |
| push uses `--force-with-lease` | Avoid overwriting someone else's production movement |
| remote production pointer verification after push | Prove the branch actually moved |
| remote tag verification after push | Prove release metadata exists |
| interactive confirmation | Make shipping explicit |

### Step 4: Add status/check scripts and templates

Recommended optional files:

```text
scripts/check_release_status.sh
.github/pull_request_template.md
.github/workflows/verify-production-pointer.yml
```

Use these skill files:

- `scripts/check_release_status.sh` → copy to target repo `scripts/check_release_status.sh` and `chmod +x`.
- `templates/release-pr-template.md` → copy to `.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE/release.md`.
- `templates/verify-production-pointer.yml` → copy to `.github/workflows/verify-production-pointer.yml`.

The workflow is verification-only: it checks that `production` remains reachable from `main` and shows divergence. It does not deploy and requires no secrets.

### Step 5: Add or update deployment docs

Use `assets/DEPLOY-snippet.md` for a concise `docs/DEPLOY.md` or README section.

Use `assets/BRANCHING_AND_DEPLOYMENT_STRATEGY.md` for a longer branch strategy guide when the repo has team/process documentation.

Make sure the docs say:

- This workflow is opinionated and should be read before cutover.
- `main` is the canonical latest-code / release-candidate branch.
- `main` is not guaranteed to equal live production.
- `production` is a pointer branch, not a working branch.
- The host's Production Branch must be `production` after cutover.
- `run_deploy.sh` advances `production` from `main` and creates a release tag.
- The production branch movement triggers the host deploy; the tag is release metadata unless the host/tooling says otherwise.

### Step 6: Land tooling via PR; do not cut over silently

Create a feature branch from the repo's normal integration branch:

```bash
git switch develop  # if the project uses develop
git pull --ff-only origin develop
git switch -c feat/setup-release-pipeline
```

If no `develop` exists, branch from `main`.

Commit the script/docs/templates and open a PR. The PR should be inert: merging the script/docs must not change production behavior by itself.

Suggested PR title:

```text
chore(deploy): add explicit production pointer release workflow
```

PR body should include:

- What changes: script + docs/templates only.
- Why: decouple merging to `main` from shipping to users.
- Manual cutover steps the user must perform after merge.
- Rollback/hotfix notes.
- Branch protection expectations for `production`.

### Step 7: Manual cutover

The user changes the host dashboard. Do not claim this is done unless you can actually verify it.

Recommended cutover:

1. Ensure `main` is the intended current release candidate.
2. Create `production` from current `main` if absent:
   ```bash
   git fetch origin
   git push origin origin/main:refs/heads/production
   ```
3. In the host dashboard, change Production Branch from `main` to `production`.
4. Confirm a deployment from `production` succeeds and points at the expected commit.
5. Add branch protection / permissions for `production`:
   - restrict who can push/move it;
   - allow release maintainers to move it with `run_deploy.sh`;
   - do not require normal PR flow on `production`;
   - avoid redundant required checks on `production` if `main` already passed CI;
   - prevent branch deletion if possible.
6. Future releases are cut from `main` using:
   ```bash
   git switch main
   git pull --ff-only origin main
   ./run_deploy.sh 0.1.0
   ```

### Step 8: Verify behavior

After cutover, verify with the user:

- A merge/push to `main` no longer changes the live production URL.
- `./run_deploy.sh <version>` moves `production` to `main` and triggers the host production deployment.
- The host deployment page shows source/ref `production` for the live deploy.
- The release tag exists and points to the same commit as the release.
- `scripts/check_release_status.sh` reports the expected divergence.
- Optional GitHub Actions verification passes without secrets.

## Branch Protection Guidance

`production` is not a review branch. It is a live pointer.

Recommended settings:

| Branch | Protection intent |
| --- | --- |
| `develop` | Normal PR reviews and tests for daily integration. |
| `main` | Release-candidate PR reviews and stronger checks. |
| `production` | Restrict who can move it; do not make normal PR flow mandatory. |

For `production`, prefer:

- restrict push access to release maintainers/admins;
- block deletion;
- allow the release maintainer to use `--force-with-lease` if the platform requires pointer movement;
- do not require PRs into `production`;
- do not require duplicate status checks if `main` already passed them;
- document that emergency direct production changes must be back-ported immediately.

If org policy forbids force pushes entirely, this strategy may need adaptation: use a PR/merge into `production`, a GitHub Environment deployment workflow, or a host-supported manual promote feature instead.

## Hotfix Policy

Normal feature/fix/docs branches start from `develop`. Production hotfixes are the explicit exception.

Preferred hotfix path:

```text
fix/* from main
→ PR to main
→ review
→ merge to main
→ ./run_deploy.sh <patch-version>
→ merge/cherry-pick the fix back to develop if develop exists
```

Emergency direct-to-`production` changes should be rare. If they happen, immediately back-port the same commit to `main` and `develop`. Otherwise the invariant check will fail later, or worse, a future release can drop the emergency fix.

## Rollback Policy

Rollback by moving `production` back to a previous good tag/commit:

```bash
git fetch origin --tags
git tag -l 'v*' --sort=-version:refname | head -5
GOOD_SHA="$(git rev-list -n 1 v0.1.2)"

# Safety: rollback target must still be part of main history.
git merge-base --is-ancestor "$GOOD_SHA" origin/main

git push --force-with-lease origin "$GOOD_SHA":refs/heads/production
```

The host redeploys from the rewound `production` pointer. `main` remains untouched for investigation and follow-up fixes.

## Common Mistakes

- **Treating `production` as a normal branch.** It is a release pointer. Work happens on `develop`, `feat/*`, `fix/*`, and release PRs into `main`.
- **Forgetting that `main` may be ahead of live.** Only `production` reflects live after cutover.
- **Saying tag push triggers deploy.** In this model, the push to `production` triggers the host deploy. The tag is release metadata unless the project has separate tag-triggered automation.
- **Skipping host dashboard cutover.** If the host still watches `main`, merging to `main` still ships.
- **Breaking the invariant with hotfixes.** Always back-port emergency production fixes to `main` and `develop`.
- **Over-protecting `production`.** Requiring PRs/status checks on a pointer branch can block the release script. Protect it by restricting who can move it, not by making normal PR flow mandatory.
- **Tag push fails after production moved.** The live deploy may already be running. Retry `git push origin vX.Y.Z`; if the local tag is wrong, delete it with `git tag -d vX.Y.Z` before rerunning.
- **Ignoring preview builds.** This strategy controls production reflection. It may not eliminate provider preview builds for `main` or PR branches.

## Files in This Skill

- `assets/run_deploy.sh` — drop-in production pointer release script with diff summary and remote verification.
- `assets/DEPLOY-snippet.md` — concise deployment documentation sections.
- `assets/BRANCHING_AND_DEPLOYMENT_STRATEGY.md` — longer strategy guide for teams/agents.
- `scripts/check_release_status.sh` — local/CI divergence and invariant checker.
- `templates/release-pr-template.md` — release PR checklist template.
- `templates/verify-production-pointer.yml` — secret-free GitHub Actions verification workflow.
