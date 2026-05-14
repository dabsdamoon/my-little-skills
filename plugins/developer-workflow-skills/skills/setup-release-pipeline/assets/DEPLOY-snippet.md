<!--
Drop-in chunks for a repo's docs/DEPLOY.md, README, or agent instructions.
Replace <HOST> with Vercel / Netlify / Render / etc. Remove sections that do not apply.
-->

## Branch model

This workflow is simple but opinionated. Read the trade-offs before cutover.

This project separates "latest code" from "live production".

| Branch | Role | Deploy hook |
| --- | --- | --- |
| `develop` | Development integration and QA/QC. All `feat/*`, `fix/*`, `docs/*`, and `chore/*` branches PR into here. | Optional staging/preview/CI only |
| `main` | Canonical latest-code branch and release candidate. GitHub default branch. **Merging to `main` does not mean users see it.** | No production deploy after cutover |
| `production` | Live reflection branch / release pointer. Always points to a commit already reachable from `main`. | **<HOST> watches this branch for production deploys.** |

If the project has no `develop` branch, use `main` as the integration/release-candidate branch and keep `production` as the live pointer.

## Core invariant

`production` is not a normal working branch. It is a pointer moved by `./run_deploy.sh` during normal releases.

```text
production must always be reachable from main
```

Immediately after a release, `production` and `main` may point to the same commit.

If an emergency fix is pushed directly to `production`, back-port it to `main` and `develop` immediately. Otherwise the next normal release can drop the fix.

## Host configuration

In <HOST>'s project settings, set the Production Branch / production deploy branch to:

```text
production
```

After cutover:

```text
main push/merge       → latest code only, not live production
production branch move → <HOST> production deploy
```

Confirm in the host dashboard that the latest production deployment source/ref is `production`, not `main`.

## Releasing

From local `main`, up to date:

```bash
git switch main
git pull --ff-only origin main

./run_deploy.sh          # inspect: previous tags, suggested next version, release diff, divergence
./run_deploy.sh 0.1.0    # release: production moves to main HEAD, then tags
```

Optional status check before deciding whether to release:

```bash
scripts/check_release_status.sh
```

The script asks for confirmation before pushing. It refuses if:

- local branch is not `main`
- working tree is dirty
- local `main` differs from `origin/main`
- `origin/production` has commits not on `origin/main`
- tag format is not `x.y.z`
- local or remote tag already exists

Before confirmation, it prints the pending release count, oldest pending commit, commit list, and file diff summary for `origin/production..origin/main`. After pushing, it verifies that `origin/production` equals `origin/main` and that the release tag exists remotely.

What deploys?

```text
./run_deploy.sh <version>
→ git push origin <main-sha>:production
→ <HOST> sees production branch move
→ <HOST> production build/deploy runs
→ vX.Y.Z tag is pushed as release metadata
```

In this model, the `production` branch movement triggers the host production deploy. The version tag is release metadata unless this project also has separate tag-triggered automation.

## Branch protection

Recommended protection model:

### `develop`

- Require PRs for feature/fix/docs work if the team uses reviews.
- Require tests/lint where available.

### `main`

- Require PR before merging.
- Prefer `develop → main` release PRs.
- Allow urgent `fix/* → main` PRs for hotfixes.
- Require CI/status checks if configured.

### `production`

- Treat as a release pointer, not a code review branch.
- Restrict who can push/move it.
- Block branch deletion if possible.
- Allow the release maintainer to use the `run_deploy.sh` pointer move.
- Do not require normal PR flow on `production`.
- Avoid redundant required checks on `production` if the same commit already passed on `main`.
- If org policy forbids force pushes entirely, adapt the workflow to use PR/merge into `production`, GitHub Environments, or host-level manual promotion instead.

## One-time cutover

If <HOST> currently deploys from `main`, perform these once after the script/docs PR is merged.

1. Ensure `main` is the commit you are comfortable making live.
2. Create `production` from current `main` if it does not exist:

   ```bash
   git fetch origin
   git push origin origin/main:refs/heads/production
   ```

3. In <HOST>'s dashboard, change Production Branch from `main` to `production`.
4. Confirm the deployment is from the expected commit/ref.
5. Add branch protection/permissions for `production`.
6. Future releases use:

   ```bash
   git switch main
   git pull --ff-only origin main
   ./run_deploy.sh <next-version>
   ```

## Rollback

Rollback means moving the live pointer back to a known-good tag/commit.

```bash
git fetch origin --tags
git tag -l 'v*' --sort=-version:refname | head -5

GOOD_SHA="$(git rev-list -n 1 v0.1.2)"   # replace with last good tag

# Safety: rollback target must still be part of main history.
git merge-base --is-ancestor "$GOOD_SHA" origin/main

git push --force-with-lease origin "$GOOD_SHA":refs/heads/production
```

<HOST> redeploys from the rewound `production` pointer. `main` is untouched so the bad release can be investigated there.

## Hotfixes

Preferred path:

```text
fix/* from main
→ PR to main
→ review/merge
→ ./run_deploy.sh <patch-version>
→ back-port to develop if needed
```

Emergency direct-to-`production` changes are allowed only when unavoidable. If used, immediately back-port the fix to `main` and `develop`.
