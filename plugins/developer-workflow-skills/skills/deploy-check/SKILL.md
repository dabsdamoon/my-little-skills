---
name: deploy-check
description: Pre-merge production safety analysis. Scans git diff for destructive changes, breaking API contracts, missing migrations, environment dependencies, and rollback risks before deploying to production.
license: Complete terms in LICENSE.txt
---

# Deploy Check — Pre-Merge Production Safety Analysis

Analyze a git diff between branches to identify destructive or dangerous changes before merging to production. This skill is conservative by design — flag uncertain items as CAUTION rather than miss real issues.

## When to Use

- Before merging `dev` → `main` (or any branch → production)
- Before deploying to a live environment with no developer available
- When reviewing changes that touch critical paths (payments, auth, data, cron jobs)

## Arguments

The skill accepts branch names in the format: `<source> to <target>`

Examples:
- `dev to main`
- `feat/my-feature to dev`

If no arguments provided, default to `dev to main`.

## Process

### Step 1: Gather Changes

Run these commands **in parallel** to understand the diff:

```bash
git log <target>..<source> --oneline          # Commit history
git diff <target>...<source> --name-status    # Changed files
git diff <target>...<source> --stat           # Change statistics
```

### Step 2: Categorize and Analyze

For each changed file, classify by risk category and run the corresponding checks.

#### Category 1: Database & Schema Changes (CRITICAL)

**Scan for:**
- Changes to schema files (`schema.ts`, `*.sql`, migration files)
- `DROP TABLE`, `DROP COLUMN`, `ALTER TABLE ... DROP`, `RENAME`
- Changes to indexes, constraints, or foreign keys
- New tables without corresponding migration files
- `DELETE FROM` or `UPDATE` without WHERE clause in server files

**Check commands:**
```bash
git diff <target>...<source> -- "**/schema*" "**/migration*" "**/*.sql"
git diff <target>...<source> | grep -iE "(DROP|ALTER|DELETE FROM|UPDATE.*SET)" | grep -v "test"
```

**Risk levels:**
- DROP/DELETE/RENAME → DANGER
- New column with NOT NULL and no default → DANGER
- New migration file → CAUTION (verify it runs cleanly)
- Schema change with no migration → CAUTION
- Additive changes only (new tables, new columns with defaults) → SAFE

#### Category 2: API Contract Changes (HIGH)

**Scan for:**
- Changed route files (`routes/api/**`, `routes/*.tsx`)
- Modified loader/action return shapes
- Removed or renamed exports
- Changed request/response types

**Check commands:**
```bash
git diff <target>...<source> -- "app/routes/**"
```

**Look for:**
- Removed fields from loader return objects → DANGER
- Changed field names or types → DANGER
- New required fields in request body → CAUTION
- Additive fields only → SAFE

#### Category 3: Environment & Configuration (HIGH)

**Scan for:**
- New `process.env.*` references
- Changes to `.env.example`, `docker-compose.yml`, Dockerfile
- Changed Terraform/infrastructure files
- Modified CI/CD workflows (`.github/workflows/`)

**Check commands:**
```bash
git diff <target>...<source> | grep -n "process\.env\." | head -20
git diff <target>...<source> -- ".env*" "docker*" "terraform/**" ".github/**"
```

**Risk levels:**
- New required env var not in deployment config → DANGER
- Changed CI/CD pipeline → CAUTION
- New optional env var with fallback → SAFE

#### Category 4: Data Integrity & Side Effects (HIGH)

**Scan for:**
- Changes to cron jobs / scheduler (`scheduler*.ts`, `*-expiration*.ts`)
- Modified notification logic (SMS, email, push)
- Payment flow changes
- Bulk data operations

**Check commands:**
```bash
git diff <target>...<source> -- "**/scheduler*" "**/cron*" "**/*expiration*" "**/payment*" "**/sms*" "**/email*"
```

**Risk levels:**
- Changed cron schedule → CAUTION
- Modified payment flow → DANGER
- Changed notification templates/logic → CAUTION
- New cron job → CAUTION

#### Category 5: Authentication & Security (CRITICAL)

**Scan for:**
- Changes to auth/session files
- Modified middleware or guards
- New endpoints without auth checks
- Secrets in diff

**Check commands:**
```bash
git diff <target>...<source> -- "**/auth/**" "**/session*" "**/middleware*"
git diff <target>...<source> | grep -iE "(password|secret|token|api_key|private_key)\s*[=:]" | grep -v "\.(md|txt|example|test):"
```

**Risk levels:**
- Exposed secrets → DANGER (block merge)
- Changed auth logic → DANGER
- New unprotected endpoint → CAUTION
- Auth-related test changes only → SAFE

#### Category 6: Rollback Assessment

For each finding, assess:
- **Can this be rolled back** by reverting the merge commit?
- **Are there one-way operations** (data migrations, sent notifications, deleted records)?
- **What is the blast radius** if rolled back? (data loss, user-facing errors, silent corruption)

### Step 3: Score Overall Risk

Based on findings:

| Score | Criteria | Action |
|-------|----------|--------|
| **SAFE** | All categories SAFE, no CAUTION/DANGER findings | Merge freely |
| **CAUTION** | 1+ CAUTION findings, no DANGER | Review findings, merge with awareness |
| **DANGER** | 1+ DANGER findings | Address findings before merge |

### Step 4: Generate Report

Output the report in this exact format:

```markdown
## Deploy Safety Report

**Risk Level:** [SAFE / CAUTION / DANGER]
**Branch:** `<source>` → `<target>`
**Date:** YYYY-MM-DD
**Files Changed:** N (X new, Y modified, Z deleted)
**Commits:** N

---

### Findings

| # | Category | Finding | Severity | File | Action Required |
|---|----------|---------|----------|------|-----------------|
| 1 | ... | ... | DANGER/CAUTION/SAFE | path/to/file | What to do |

[If no findings:]
> No dangerous or cautionary changes detected.

---

### Changed File Classification

| File | Category | Risk |
|------|----------|------|
| path/to/file | DB/API/Env/Data/Auth/Other | SAFE/CAUTION/DANGER |

---

### Pre-Deploy Checklist

[Generate based on findings. Always include:]
- [ ] All CI tests passing
- [ ] Typecheck passing
- [ ] No secrets in diff
[Add conditional items based on findings, e.g.:]
- [ ] Run migration on staging first
- [ ] Verify new env var is set in production
- [ ] Notify admin team about behavior change

---

### Rollback Plan

**Reversibility:** [Fully reversible / Partially reversible / Irreversible]

[If fully reversible:]
> Revert the merge commit. No data migrations or one-way operations.

[If partially/irreversible, describe:]
> 1. What can be reverted
> 2. What cannot (and why)
> 3. Manual steps needed after revert

---

### Impact Summary

**User-facing changes:**
- [List what users will see differently, or "None"]

**Admin-facing changes:**
- [List what admins will see differently, or "None"]

**Background/cron changes:**
- [List scheduler/notification changes, or "None"]
```

## Guidelines

### Conservative Bias
- When in doubt, flag as CAUTION
- False positives are acceptable; false negatives are not
- An unnecessary warning costs 5 seconds to dismiss; a missed issue costs hours to debug in production

### Context Awareness
- Read CLAUDE.md for project-specific conventions
- Check the project's deployment strategy (container restart? blue-green? rolling?)
- Consider what time the deploy happens (during business hours? off-hours?)

### What This Skill Does NOT Cover
- Runtime performance (use load testing)
- Visual regression (use screenshot comparison)
- Live endpoint health (use uptime monitoring)
- User acceptance (use manual QA)

This skill covers **code-level pre-merge analysis only**.

## Keywords

deploy, deployment, merge, production, safety, risk, pre-merge, review, check, analysis, rollback, migration, breaking change
