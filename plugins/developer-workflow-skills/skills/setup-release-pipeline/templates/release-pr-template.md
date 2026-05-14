## Release Candidate

Promotes `develop` into `main` as the latest-code / release-candidate branch.

> Note: merging this PR does **not** ship to users after the production-pointer cutover. Production ships only when `./run_deploy.sh <version>` advances the `production` branch.

## Release scope

- 

## QA/QC completed

- [ ] Local build passes
- [ ] Local tests/lint pass where available
- [ ] Staging/preview checked, if configured
- [ ] Mobile/responsive check completed, if UI-facing
- [ ] Accessibility/basic UX check completed, if UI-facing
- [ ] No secrets or environment-specific values committed

## Risk level

- [ ] Low
- [ ] Medium
- [ ] High

Why:


## Production release plan

Target version:

```text
v0.0.0
```

After merge to `main`:

```bash
git switch main
git pull --ff-only origin main
./run_deploy.sh 0.0.0
```

## Rollback plan

Previous known-good tag/commit:

```text
v0.0.0 / <sha>
```

Rollback command, if needed:

```bash
git fetch origin --tags
git merge-base --is-ancestor <good-sha> origin/main
git push --force-with-lease origin <good-sha>:refs/heads/production
```

## Reviewer notes

- Confirm PR base is `main` and source is usually `develop`.
- Confirm `production` is not directly edited by this PR.
- Confirm the release can be safely held after merge if final production deploy is delayed.
