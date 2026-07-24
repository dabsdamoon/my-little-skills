# Git interpretation rules

## What Git can support

Git can directly support claims about recorded commits, parents, authorship
metadata, committer timestamps, tags, reachable refs, changed paths, and
numstat. Repository documentation and merge messages can support product and
decision context when cited as separate sources.

## What Git cannot prove

Do not infer these from Git alone:

- Hours, person-days, or labor cost.
- Individual productivity or performance.
- Work performed in meetings, design tools, issue trackers, or uncommitted
  environments.
- Feature completeness, correctness, production use, or business impact.
- Original development date after a rebase, squash, import, or history rewrite.

## History-shape caveats

- A squash merge compresses many changes into one commit.
- A merge commit can cause churn totals to overlap child commits.
- Rebases rewrite object IDs and committer dates.
- Cherry-picks duplicate logical work under different object IDs.
- `--all-refs` includes activity that may never have shipped.
- A shallow clone omits earlier reachable history.
- Deleted remote branches may no longer be discoverable.

Disclose applicable caveats in both the evidence record and report.

## Privacy and security

- Redact author email addresses by default.
- Treat names, branch names, remotes, paths, and commit subjects as potentially
  sensitive.
- Do not include patch contents in evidence by default.
- Review external reports for customer names, credentials, vulnerability
  details, protected health information, and other regulated data.
- Keep the internal report within the audience authorized for repository
  access.
