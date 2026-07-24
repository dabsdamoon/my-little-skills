# Git evidence schema

`git-evidence.json` uses schema
`https://dabsdamoon.github.io/schemas/git-work-report-evidence-v1.json`.

## Top-level fields

| Field | Meaning |
|---|---|
| `schema` | Stable schema identifier. Reject unknown values. |
| `generated_at` | UTC collection timestamp in ISO 8601 form. |
| `repository` | Repository name, absolute root, Git version, remotes, and working-tree state. |
| `scope` | Revision expression, resolved tip, filters, timezone, and all-refs flag. |
| `completeness` | Shallow/truncated state, total matching commits, and warnings. |
| `summary` | Reproducible aggregate metrics derived from `commits`. |
| `contributors` | Author groups with email hashes and optional clear addresses. |
| `activity` | Commit counts grouped by reporting-zone calendar date. |
| `tags` | Tags whose target commits are present in the collected commit set. |
| `refs` | Local and remote ref snapshot used to describe collection state. |
| `commits` | Commit-level evidence in Git log order. |

## Commit fields

Each commit contains:

- Full and short object IDs.
- Parent object IDs and merge status.
- Author and committer names, email fingerprints, and ISO timestamps.
- Activity date converted into `scope.timezone`.
- Subject, decorations, and normalized change category.
- Insertions, deletions, binary-file count, file count, and changed paths.

The collector uses committer time for the chronological work log because it
describes when the change entered the recorded history. Author time remains
available for audit purposes.

## Metric definitions

- `commit_count`: unique commits reachable within the selected revision and
  filters.
- `merge_commit_count`: commits with two or more parents.
- `numbered_merge_commit_count`: merge subjects containing a PR-like number.
- `activity_day_count`: unique reporting-zone committer dates.
- `tag_count`: tags whose target commits are present in the collected scope.
- `insertions` and `deletions`: sums of per-commit numstat values. These are
  churn indicators and can double-count changes across merges or reversions.
- `unique_path_count`: distinct changed paths observed in commit numstats.

Do not describe summed numstat as net codebase growth.
