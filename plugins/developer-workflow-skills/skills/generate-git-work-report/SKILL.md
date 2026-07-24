---
name: generate-git-work-report
description: Generate repeatable, evidence-backed project execution histories and detailed work logs from a local Git repository, including polished reference-matched DOCX/PDF deliverables. Use when a user asks for a Git-based 수행이력, 업무일지, work log, project history, delivery report, audit trail, external project summary, internal evidence report, or professionally formatted office report derived from commit, merge, tag, author, date, and file-change history.
---

# Generate Git Work Report

Create two reports from one immutable Git evidence snapshot:

- An external summary that explains scope, milestones, outcomes, and validation
  without exposing unnecessary internal detail.
- An internal work log that preserves chronological commit-level traceability.

Treat Git as evidence of recorded change, not proof of hours worked, effort,
individual productivity, business value, or work performed outside the
repository.

Keep the evidence workflow deterministic. Treat editorial interpretation and
office-document design as separate, explicit stages with their own gates.

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

### 5. Build the report story

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

Before office authoring, write a short story map for each report:

- External: cover decision, executive summary, milestone narrative,
  quantitative evidence, validation/handoff, limitations.
- Internal: evidence boundary, aggregate map, chronological phases,
  commit-complete appendix, warnings and supporting artifacts.
- Assign a page budget to each major section. Do not convert the Markdown
  linearly without deciding which content belongs in prose, callouts, tables,
  timelines, or appendices.

Read `references/report-templates.md` for the required content architecture.

Do not claim elapsed effort, staffing level, completion percentage, cost, or
causality from commit counts alone.

### 6. Verify the canonical reports

Run after all Markdown edits:

```bash
python3 "$SKILL_DIR/scripts/verify_work_reports.py" \
  --evidence "$OUTPUT_DIR/git-evidence.json" \
  --external "$OUTPUT_DIR/external-project-history.md" \
  --internal "$OUTPUT_DIR/internal-work-log.md" \
  --output "$OUTPUT_DIR/verification.json"
```

The command must pass before office authoring. It checks:

- Evidence fingerprints in both reports.
- Metric consistency.
- One-to-one internal commit coverage.
- Duplicate or unknown commit markers.
- Placeholders.
- Shallow or truncated evidence.

If editorial changes intentionally alter a machine-generated number, recollect
or rerender instead of hand-editing the metric marker.

### 7. Create DOCX or PDF when requested

Treat the Markdown reports and `git-evidence.json` as the canonical record.
Read `references/office-delivery.md` completely before creating an office
artifact. Select exactly one mode:

- **Reference-first mode:** mandatory when the user supplies or points to a
  DOCX, PDF, report family, or visual example. The retained reference controls
  page geometry, typography, colors, cover, tables, headers, footers, spacing,
  and component rhythm. Do not read or apply the neutral theme first.
- **Neutral fallback mode:** use only when there is no visual reference. Read
  `assets/neutral-report-theme.json` and apply it as a complete token set.

In reference-first mode:

1. Use the available document and PDF skills.
2. Retain the reference unchanged and render every reference page.
3. Create a task-local `artifact.md` that records reference hashes, page count,
   geometry, typography, palette, tables, page furniture, content flow, and
   intentional brand/content substitutions.
4. Reuse the reference style system faithfully. Replace its product identity,
   confidential data, quoted prices, and proprietary content with the target
   project's material; do not weaken template fidelity merely because the
   identity changes.
5. Prefer a sibling DOCX as the implementation authority when the user points
   to a PDF. If only a PDF exists, distill the rendered pages before authoring.

For both modes:

1. Keep Markdown, DOCX, and PDF basenames/version labels aligned.
2. Use the DOCX as the editable office source and generate the PDF from the
   latest DOCX.
3. Render every final page. Iterate after each meaningful layout change.
4. Reject accidental blank pages, isolated callouts, continuation-only pages,
   short tables split across pages, clipped text, broken glyphs, inconsistent
   headers/footers, unresolved placeholders, and raw Markdown residue.
5. Inspect at 100% zoom. A contact sheet is navigation, not a substitute for
   per-page review.
6. Run the office preflight after visual inspection:

```bash
python3 "$SKILL_DIR/scripts/verify_office_delivery.py" \
  --pair "external=$OUTPUT_DIR/external-project-history.docx,$OUTPUT_DIR/external-project-history.pdf" \
  --pair "internal=$OUTPUT_DIR/internal-work-log.docx,$OUTPUT_DIR/internal-work-log.pdf" \
  --reference-mode \
  --template-audit "$OUTPUT_DIR/artifact.md" \
  --visual-qa-confirmed \
  --output "$OUTPUT_DIR/office-verification.json"
```

Omit `--reference-mode` and `--template-audit` only for neutral fallback mode.
The preflight complements, but never replaces, visual inspection.

## Delivery checklist

- State the repository, revision scope, period, timezone, and evidence
  fingerprint.
- Distinguish external summary from internal evidence.
- Disclose shallow clones, filters, missing refs, squashes, rebases, and other
  known limitations.
- Confirm both Markdown evidence verification and office preflight results.
- Confirm final DOCX/PDF page counts and full-page visual QA.
- State whether reference-first or neutral fallback mode was used.
- Keep generated reports outside the source repository unless the user
  specifies a tracked documentation path.
