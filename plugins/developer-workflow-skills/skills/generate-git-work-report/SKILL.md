---
name: generate-git-work-report
description: Generate repeatable, evidence-backed project execution histories and detailed work logs from a local Git repository. Use when a user asks for a Git-based 수행이력, 업무일지, work log, project history, delivery report, audit trail, external project summary, internal evidence report, or DOCX/PDF report derived from commit, merge, tag, author, date, and file-change history.
---

# Generate Git Work Report

Create two reports from one immutable Git evidence snapshot:

- An external summary that explains scope, milestones, outcomes, and validation
  without exposing unnecessary internal detail.
- An internal work log that preserves chronological commit-level traceability.

Treat Git as evidence of recorded change, not proof of hours worked, effort,
individual productivity, business value, or work performed outside the
repository.

## Workflow

### 1. Define the evidence boundary

Determine or state these inputs before collecting evidence:

- Repository path.
- Revision scope. Default to the current `HEAD`; use `--all-refs` only when the
  user explicitly wants unmerged or orphaned branch activity included.
- Optional date and author filters.
- Reporting timezone. Default to `UTC` when the user gives no locale.
- Output directory, project name, and language.
- Whether author email addresses may be retained. Keep them redacted by
  default.

Do not silently combine `HEAD`, all refs, the working tree, GitHub activity, or
chat history. Report each evidence source separately.

### 2. Collect the canonical evidence

Set `SKILL_DIR` to this skill directory, then run:

```bash
python3 "$SKILL_DIR/scripts/collect_git_evidence.py" \
  --repo "$REPO_PATH" \
  --ref HEAD \
  --timezone +09:00 \
  --output "$OUTPUT_DIR/git-evidence.json"
```

Use an IANA zone such as `Asia/Seoul` when timezone data is available, or a
fixed offset such as `+09:00` for a portable snapshot. Use `--since`,
`--until`, or `--author` only when requested. Use
`--include-author-email` only with an explicit need for personally identifiable
information.

Stop and disclose the limitation when the collector reports a shallow
repository, truncation, an unresolved revision, or an empty scope. Do not fill
history gaps with inference.

### 3. Read the evidence and repository context

Read:

- `references/interpretation-rules.md` before making narrative claims.
- `references/report-templates.md` before editing either report.
- `references/evidence-schema.md` when consuming fields beyond the summary
  metrics or when extending a script.

Inspect the repository's README, agent guidance, product state, ADRs, release
notes, and substantive merge messages. Use these sources to explain what the
work means. Keep every number, date, tag, and commit claim anchored to
`git-evidence.json`.

### 4. Generate deterministic first drafts

Run:

```bash
python3 "$SKILL_DIR/scripts/render_work_reports.py" \
  --evidence "$OUTPUT_DIR/git-evidence.json" \
  --output-dir "$OUTPUT_DIR" \
  --project-name "$PROJECT_NAME" \
  --language ko
```

This creates:

- `external-project-history.md`
- `internal-work-log.md`

The internal draft contains one machine-readable marker for every commit in
scope. Preserve these markers while editing so coverage remains verifiable.

### 5. Add editorial interpretation

Improve the deterministic draft without changing its evidence contract:

- External report: add the product purpose, delivery scope, major milestones,
  user or operational outcomes, validation, exclusions, and a concise evidence
  basis.
- Internal report: add decision context, verification details, incident or
  release links, and fact-versus-interpretation labels where useful.
- Prefer grouped milestones over a raw commit list in the external report.
- Keep exact commit hashes and chronological coverage in the internal report.
- Remove internal paths, author identities, security-sensitive messages, and
  customer data from the external version unless explicitly authorized.

Do not claim elapsed effort, staffing level, completion percentage, cost, or
causality from commit counts alone.

### 6. Create DOCX or PDF when requested

Treat the Markdown reports and `git-evidence.json` as the canonical record.
When office documents are requested:

1. Use the available document/PDF skill or renderer.
2. Read `assets/neutral-report-theme.json`.
3. Use A4 portrait, restrained neutral colors, black table headers, horizontal
   separators, quiet page numbering, and generous white space by default.
4. If the user supplies a visual reference, reuse structural principles only;
   do not copy logos, identities, quoted prices, or proprietary branding.
5. Render every page and inspect for clipping, broken tables, missing glyphs,
   accidental blank pages, and unresolved placeholders.

### 7. Verify the reports

Run after all Markdown edits:

```bash
python3 "$SKILL_DIR/scripts/verify_work_reports.py" \
  --evidence "$OUTPUT_DIR/git-evidence.json" \
  --external "$OUTPUT_DIR/external-project-history.md" \
  --internal "$OUTPUT_DIR/internal-work-log.md" \
  --output "$OUTPUT_DIR/verification.json"
```

The command must pass before delivery. It checks:

- Evidence fingerprints in both reports.
- Metric consistency.
- One-to-one internal commit coverage.
- Duplicate or unknown commit markers.
- Placeholders.
- Shallow or truncated evidence.

If editorial changes intentionally alter a machine-generated number, recollect
or rerender instead of hand-editing the metric marker.

## Delivery checklist

- State the repository, revision scope, period, timezone, and evidence
  fingerprint.
- Distinguish external summary from internal evidence.
- Disclose shallow clones, filters, missing refs, squashes, rebases, and other
  known limitations.
- Confirm the verifier result and any visual QA performed.
- Keep generated reports outside the source repository unless the user
  specifies a tracked documentation path.
