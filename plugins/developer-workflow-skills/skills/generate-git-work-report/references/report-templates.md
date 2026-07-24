# Report templates

## External project history

Use this order unless the user's submission format requires another:

1. Document identity and evidence baseline.
2. Project purpose and delivery scope.
3. Reporting period and explicit exclusions.
4. Major milestones grouped by user or operational outcome.
5. Quantitative activity summary with careful metric definitions.
6. Validation, release state, and handoff.
7. Evidence basis and limitations.

Keep commit hashes, contributor identities, internal paths, and raw commit
messages out of the body unless they are required by the recipient. A short
evidence fingerprint is normally sufficient.

## Internal detailed work log

Use this order:

1. Evidence snapshot and collection command.
2. Completeness and repository-state warnings.
3. Aggregate metrics and metric definitions.
4. Chronological entries grouped by reporting-zone date.
5. For every commit: full evidence marker, visible short hash, subject,
   category, author, changed-file count, numstat, and representative paths.
6. Release tags, branch/ref snapshot, and validation record.
7. Interpretation notes, unresolved gaps, and supporting artifact paths.

Preserve `<!-- commit:FULL_HASH -->`, `<!-- evidence-sha256:... -->`, and
`<!-- metric:key=value -->` comments. The verifier depends on them.

## Writing rules

- Label statements as fact, interpretation, or user-provided context when the
  distinction is material.
- Prefer exact dates and revision names over words such as "recently".
- Explain why a milestone mattered; do not merely restate a commit subject.
- Separate recorded delivery from planned or uncommitted work.
- Never equate commit frequency with effort, quality, or employee performance.
