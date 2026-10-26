# NOTICE — database-migrations

This skill is a derivative work of the `database-migrations` skill in
[everything-claude-code](https://github.com/affaan-m/everything-claude-code)
by Affaan Mustafa.

- Upstream: https://github.com/affaan-m/everything-claude-code
- Upstream path: `skills/database-migrations/SKILL.md`
- Vendored from commit `0765f7a2ca2bd5df214d3aa7ba7e7ac19db8b189` (2026-09-27)
- Upstream license: MIT. The upstream `LICENSE` text and copyright line are
  reproduced unchanged in `LICENSE.txt` next to this file.

## What was retained from upstream

- The core principles: every change is a migration, production is
  forward-only, deployed migrations are immutable, schema and data changes are
  separate, and migrations are tested against production-sized data.
- The expand-contract pattern for zero-downtime renames, and removing code
  references before dropping a column.
- `CREATE INDEX CONCURRENTLY` for indexes on existing tables.
- Per-tool sections for Prisma, Drizzle, and golang-migrate, and the
  anti-pattern table format.

## What this fork changes, and why

Corrections (upstream text that was wrong or unsafe):

- Upstream said adding a `NOT NULL` column without a default "locks the table
  and rewrites every row". On a table with rows it errors instead. The fork
  explains the actual behavior and replaces "add nullable, backfill, then add
  constraint" with `CHECK ... NOT VALID`, then `VALIDATE CONSTRAINT`, then
  `SET NOT NULL`, which skips the table scan. It also covers the PostgreSQL 18
  `NOT NULL ... NOT VALID` form.
- Upstream called `ADD COLUMN` "no lock" and never mentioned `lock_timeout`.
  The fork adds a lock-level table and a `lock_timeout` / `statement_timeout`
  preamble.
- Upstream said a column default is instant without noting that this holds
  only for non-volatile defaults.
- Upstream's PL/pgSQL backfill used `COMMIT` inside a `DO` block meant to run
  as a migration. That fails inside the migration tool's transaction, and its
  loop never ended when the computed value stayed NULL. The fork runs a keyset
  loop through `psql`, outside any migration, that ends and can be rerun.
- Upstream's Django backfill could also loop forever (when the copied
  `username` was empty) and ran in a single transaction. Django was dropped
  (see below).
- Upstream's expand-contract example backfilled before the dual-write deploy,
  which loses rows written in between. The fork orders dual-write first.
- Upstream's golang-migrate example put `ADD COLUMN` and
  `CREATE INDEX CONCURRENTLY` in one file. The driver runs a file as one
  transaction, so that fails. The fork moves `CONCURRENTLY` to its own file.
- Upstream used `CREATE INDEX CONCURRENTLY IF NOT EXISTS`, which silently keeps
  an INVALID index left by a failed build. The fork adds an `indisvalid` check
  and recovery steps.
- Upstream required DOWN migrations while also saying production is
  forward-only. The fork limits down migrations to local development.

Scope changes for the maintainer's stack (Python, TypeScript/Node, Go,
Supabase/Postgres, GCP Cloud Run):

- Added a Supabase CLI section (`migration new`, `db diff`, `db push --dry-run`,
  `db reset`, version notes on CONCURRENTLY) and RLS policies in migrations.
- Added Alembic. Removed Django, Kysely, and the generic MySQL framing.
- Added Prisma and Drizzle transaction notes for `CONCURRENTLY`.
- Database URLs go through the repo's `scripts/with-secrets.sh` (secrets come
  from Google Secret Manager on demand) and are never printed.
- Rewrote the description so pre-merge diff review goes to `deploy-check`.

Every API, command, flag, lock level, and version in `SKILL.md` was checked
against the sources in its "Sources" section on 2026-10-26.
