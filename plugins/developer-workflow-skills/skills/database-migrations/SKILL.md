---
name: database-migrations
description: "Writes Postgres and Supabase schema and data migrations without blocking production: lock_timeout, CREATE INDEX CONCURRENTLY, safe NOT NULL, expand-contract renames, batched backfills. For Supabase CLI, Prisma, Drizzle, Alembic, golang-migrate. Use when writing a migration, adding a column, index, or constraint, or backfilling a table. Not for pre-merge diff review (use deploy-check)."
---

# Database Migrations (Postgres and Supabase)

Write migrations that keep a live Postgres database serving reads and writes while the schema changes. This skill covers authoring. To review a finished branch for deploy risk before merge, use `deploy-check`.

## Rules

1. Every schema change is a migration file in the repository. Changes made in a dashboard or Supabase Studio must be captured into a migration before they count.
2. Production is forward-only. Fix a bad migration with a new migration, and never edit one that has run on a shared database. Down migrations are for local development only.
3. Keep schema changes (DDL) and large data backfills apart. Backfills run as separate batched scripts, not inside the migration tool's transaction.
4. Start every DDL file that touches an existing table with `SET lock_timeout`. The one exception is a file that holds only a `CONCURRENTLY` statement (see the tool notes).
5. Database URLs are secrets. Run commands through the repo's `scripts/with-secrets.sh`, put the variable reference inside single quotes so the child shell expands it, and never echo or print it.

## Lock reference

Every `ALTER TABLE` form takes `ACCESS EXCLUSIVE` unless the Postgres docs say otherwise. `ACCESS EXCLUSIVE` conflicts with every lock mode, including the `ACCESS SHARE` lock that a plain `SELECT` takes. The danger is the wait, not the work. A DDL statement waits indefinitely for conflicting locks, and application queries arriving after it queue behind it.

| Operation | Lock on the table | Blocks reads | Blocks writes | Notes |
|---|---|---|---|---|
| `ALTER TABLE ... ADD COLUMN`, `DROP COLUMN`, `SET NOT NULL`, `ADD CONSTRAINT ... CHECK (...) NOT VALID` | `ACCESS EXCLUSIVE` | yes | yes | Fast when no scan or rewrite is needed |
| `ALTER TABLE ... VALIDATE CONSTRAINT` | `SHARE UPDATE EXCLUSIVE` | no | no | Scans the table |
| `CREATE INDEX` | `SHARE` | no | yes | Whole build |
| `CREATE INDEX CONCURRENTLY` | `SHARE UPDATE EXCLUSIVE` | no | no | Two scans; cannot run in a transaction block |
| `DROP INDEX` | `ACCESS EXCLUSIVE` | yes | yes | Use `DROP INDEX CONCURRENTLY` on busy tables |

## Preamble for DDL on existing tables

```sql
SET lock_timeout = '5s';
SET statement_timeout = '60s';
```

`lock_timeout` aborts a statement that waits longer than the limit for any single lock. If it fires, the migration fails, nothing commits, and you retry later at a quieter time. Raise or disable `statement_timeout` (`SET statement_timeout = 0;`) only for steps that are long but do not block traffic, such as `VALIDATE CONSTRAINT`.

## Patterns

### Add a column

```sql
SET lock_timeout = '5s';

-- No rewrite: NULL is the implicit default.
ALTER TABLE users ADD COLUMN avatar_url text;

-- No rewrite: a non-volatile default is stored in the catalog.
ALTER TABLE users ADD COLUMN is_active boolean NOT NULL DEFAULT true;
```

- `ADD COLUMN ... NOT NULL` with no default fails on a table that has rows, because every existing row would be NULL. It errors; it does not rewrite. Use the NOT NULL pattern below instead.
- A volatile default rewrites the whole table and its indexes while holding `ACCESS EXCLUSIVE`. `clock_timestamp()` is the docs' example, and the same applies to any function marked VOLATILE. So do identity columns, stored generated columns, and domains with constraints. On a large table, add the column without the default and backfill it.

### Make an existing column NOT NULL

`SET NOT NULL` scans the whole table under `ACCESS EXCLUSIVE`, unless a valid `CHECK` constraint already proves there are no NULLs. Prove it first with a lighter lock:

```sql
-- Migration 1: enforced for new rows immediately; existing rows are not scanned.
SET lock_timeout = '5s';
ALTER TABLE users ADD CONSTRAINT users_role_not_null CHECK (role IS NOT NULL) NOT VALID;
```

Backfill any NULL `role` values (see "Backfill a large table").

```sql
-- Migration 2: scans under SHARE UPDATE EXCLUSIVE; reads and writes continue.
SET lock_timeout = '5s';
SET statement_timeout = 0;
ALTER TABLE users VALIDATE CONSTRAINT users_role_not_null;
```

```sql
-- Migration 3: brief ACCESS EXCLUSIVE; the table scan is skipped because the valid CHECK proves no NULLs.
SET lock_timeout = '5s';
ALTER TABLE users ALTER COLUMN role SET NOT NULL;
ALTER TABLE users DROP CONSTRAINT users_role_not_null;
```

On PostgreSQL 18 or later (check with `SHOW server_version;`), a not-null constraint itself can be added `NOT VALID` and validated later:

```sql
ALTER TABLE users ADD CONSTRAINT users_role_not_null NOT NULL role NOT VALID;
-- later migration:
ALTER TABLE users VALIDATE CONSTRAINT users_role_not_null;
```

### Add or drop an index on an existing table

```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

- `CONCURRENTLY` cannot run inside a transaction block. Put it in its own migration file, and follow the tool notes below. Most tools wrap a file in a transaction.
- Do not use `IF NOT EXISTS` as a retry. A failed concurrent build leaves an INVALID index behind, and `IF NOT EXISTS` would skip over it. After every concurrent build, check:

```sql
SELECT indexrelid::regclass AS index_name, indrelid::regclass AS table_name
FROM pg_index
WHERE NOT indisvalid;
```

  Any row means the build failed. Recover with `DROP INDEX CONCURRENTLY idx_users_email;` and then rerun the `CREATE INDEX CONCURRENTLY`, or use `REINDEX INDEX CONCURRENTLY idx_users_email;`.
- Use `DROP INDEX CONCURRENTLY` to remove an index from a busy table. It takes one index name, does not support `CASCADE`, cannot drop an index that backs a `UNIQUE` or `PRIMARY KEY` constraint, and cannot run in a transaction block.

### Rename a column or change its type (expand-contract)

Never rename in place while old code is still running. Run these steps in order:

1. **Expand (migration):** `ALTER TABLE users ADD COLUMN display_name text;`
2. **Dual-write (deploy):** the app writes both `username` and `display_name`, and still reads `username`.
3. **Backfill (script):** copy existing rows in batches after step 2 is live, so rows written during the backfill are already covered.
4. **Verify:** `SELECT count(*) FROM users WHERE display_name IS NULL AND username IS NOT NULL;` returns 0.
5. **Switch reads (deploy):** the app reads `display_name`. Then stop writing `username`.
6. **Contract (migration):** drop `username` once no deployed version reads it, including the version you would roll back to.

Backfilling before dual-write (step 3 before step 2) loses every row written in between.

### Drop a column

Remove all code references, deploy, and only then drop it in a later migration. `DROP COLUMN` takes `ACCESS EXCLUSIVE` but is quick: it hides the column and does not rewrite the table.

### Backfill a large table

Do not put this in a migration file. A `DO` block can `COMMIT` between batches only when it runs in its own transaction, not inside the migration tool's transaction. Run it with `psql` in autocommit mode, which is the default. It walks the primary key, so it ends even when the new value is NULL. It is also safe to rerun.

```sql
-- backfill_users_normalized_email.sql
DO $$
DECLARE
  last_id    users.id%TYPE;  -- NULL before the first batch
  batch_last users.id%TYPE;
BEGIN
  LOOP
    SELECT id INTO batch_last
    FROM (
      SELECT id FROM users
      WHERE last_id IS NULL OR id > last_id
      ORDER BY id
      LIMIT 5000
    ) AS batch
    ORDER BY id DESC
    LIMIT 1;

    EXIT WHEN batch_last IS NULL;  -- no rows left

    UPDATE users
    SET normalized_email = lower(email)
    WHERE (last_id IS NULL OR id > last_id)
      AND id <= batch_last
      AND normalized_email IS DISTINCT FROM lower(email);

    last_id := batch_last;
    COMMIT;
  END LOOP;
END $$;
```

```bash
scripts/with-secrets.sh sh -c 'psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f backfill_users_normalized_email.sql'
```

Do not add `-1` / `--single-transaction`. It wraps the file in one transaction, and the `COMMIT` inside the `DO` block then fails.

## Tool notes

### Supabase CLI

```bash
supabase migration new add_user_avatar   # creates supabase/migrations/<timestamp>_add_user_avatar.sql
supabase db reset                         # local only: recreate the local DB, apply all migrations, seed
supabase db diff -f add_user_avatar       # capture schema changes made locally (e.g. in Studio) as a new migration
supabase link                             # once per checkout; db push requires a linked project
supabase migration list --linked          # what the linked project has applied
supabase db push --dry-run                # print the migrations that would be applied; apply nothing
supabase db push                          # apply pending migrations to the linked project
```

- Review the `db diff` output before committing it. The legacy `migra` diff engine misses some changes: publications, storage buckets, and views with `security_invoker`.
- `supabase db reset --linked` resets the linked remote project. Never run it unless the user explicitly asks.
- Within one migration file, statements run as a batch inside an implicit transaction. Supabase CLI v2.109.0 and later run `CREATE INDEX CONCURRENTLY` (plus `REINDEX ... CONCURRENTLY`, `VACUUM`, `ALTER SYSTEM`, `CLUSTER`) outside that batch. `DROP INDEX CONCURRENTLY` gets the same handling from v2.116.0. Older CLIs fail with SQLSTATE 25001. Check the installed version before relying on this.

**RLS policies belong in migrations.** Put grants and RLS in the same migration that creates the table. With RLS enabled and no policies, nothing is reachable through the publishable key. Without RLS, a table in an exposed schema is readable and writable by any role that has a grant on it.

```sql
create table public.profiles (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users (id),
  display_name text
);

alter table public.profiles enable row level security;

create policy "Users read own profile"
  on public.profiles for select
  to authenticated
  using ( (select auth.uid()) = user_id );

create policy "Users update own profile"
  on public.profiles for update
  to authenticated
  using ( (select auth.uid()) = user_id )
  with check ( (select auth.uid()) = user_id );
```

- Name the role with `to authenticated`, and wrap `auth.uid()` in `(select ...)` so it is evaluated once per statement.
- An `UPDATE` policy needs `with check` (what the row may become) and a matching `SELECT` policy.
- A policy created in the hosted dashboard is not in any migration. Recreate it locally and capture it with `supabase db diff -f`.
- Run `supabase db reset` locally to prove the full migration chain applies from scratch.

### Prisma

```bash
npx prisma migrate dev --create-only --name add_email_index   # write migration.sql without applying it
npx prisma migrate deploy                                      # apply pending migrations (production, CI)
```

- Before Prisma ORM 7.4.0, the whole `migration.sql` was sent as one script. Several statements therefore ran as one implicit transaction. Keep `CREATE INDEX CONCURRENTLY` as the only statement in its own migration, with no `SET` line. Prisma 7.4.0 and later split the script into statements so `CONCURRENTLY` works, and the one-statement file is still the safe default.
- `prisma migrate resolve --rolled-back <name>` only records a failed migration as rolled back. It does not undo any change, and it is not a rollback tool.

### Drizzle

```bash
npx drizzle-kit generate                              # SQL migration from the schema
npx drizzle-kit generate --custom --name=users_role_check   # empty file for hand-written SQL
npx drizzle-kit migrate                               # apply pending migrations
```

- `drizzle-orm`'s migrator runs all pending migrations inside one transaction. So `CONCURRENTLY` and `COMMIT` cannot run inside Drizzle migrations. For an index on a large table, run the `CREATE INDEX CONCURRENTLY` with `psql` as a separate deploy step, then run the `indisvalid` check.
- `drizzle-kit push` writes the schema straight to the database without a migration file. Keep it to local prototyping.

### Alembic (Python / SQLAlchemy)

```bash
alembic revision --autogenerate -m "add users email index"   # review the output: autogenerate is not perfect
alembic upgrade head
alembic current
alembic history
```

```python
from alembic import op


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "idx_users_email",
            "users",
            ["email"],
            postgresql_concurrently=True,
        )
```

- `autocommit_block()` commits the transaction that came before it. When any migration uses it, set `transaction_per_migration=True` in `context.configure(...)` in `env.py`.
- Raw DDL that the operations API does not cover, such as `CHECK ... NOT VALID` or `SET lock_timeout`, goes through `op.execute("...")`.

### golang-migrate (Go)

```bash
migrate create -ext sql -dir migrations -seq add_users_email_index
scripts/with-secrets.sh sh -c 'migrate -path migrations -database "$DATABASE_URL" up'
```

- The Postgres driver runs each file in one `Exec`. Several statements in one `Exec` run inside a transaction. Put `CREATE INDEX CONCURRENTLY` alone in its own `.up.sql` file, or enable `x-multi-statement`.
- The driver has an `x-statement-timeout` URL parameter but no lock-timeout parameter, so write `SET lock_timeout` at the top of each DDL file.
- `migrate force V` only sets the recorded version after you have repaired a dirty state by hand. It runs nothing.

## Pre-apply checklist

Each item can be checked against the migration files or the database:

- [ ] Every DDL file on an existing table starts with `SET lock_timeout` (CONCURRENTLY-only files excepted).
- [ ] No `ADD COLUMN ... NOT NULL` without `DEFAULT` on a table that has rows.
- [ ] No volatile `DEFAULT` on `ADD COLUMN` for a large table.
- [ ] Every `SET NOT NULL` is preceded by a validated `CHECK (col IS NOT NULL)` (or, on PG18+, a validated `NOT NULL ... NOT VALID`).
- [ ] Indexes on existing tables use `CONCURRENTLY` in a file the tool runs outside a transaction; no `IF NOT EXISTS` retries.
- [ ] Backfills are scripts, not migration files, and are keyset-batched and rerunnable.
- [ ] Renames and drops follow expand-contract; the dropped column is unused by every deployed version and by the rollback target.
- [ ] New tables in exposed Supabase schemas enable RLS and add policies in the same migration.
- [ ] The full chain applies locally from scratch, and the production dry run (`supabase db push --dry-run` or equivalent) lists only the expected files.
- [ ] After any concurrent index build: `SELECT ... FROM pg_index WHERE NOT indisvalid` returns no rows.

Quick scan of a migrations folder:

```bash
grep -nEi 'add column[^;]*not null' supabase/migrations/*.sql | grep -vi 'default'
grep -nEi 'create (unique )?index' supabase/migrations/*.sql | grep -vi 'concurrently'
grep -nEi 'if not exists' supabase/migrations/*.sql | grep -i 'concurrently'
grep -nEi 'set not null' supabase/migrations/*.sql
```

The second check also flags indexes on brand-new tables, where a plain `CREATE INDEX` is fine.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| DDL with no `lock_timeout` | Waits forever behind a long transaction while traffic queues behind it | `SET lock_timeout` preamble, retry later |
| `SET NOT NULL` on a large table | Full scan under `ACCESS EXCLUSIVE` | `CHECK ... NOT VALID`, `VALIDATE`, then `SET NOT NULL` |
| `CREATE INDEX` on a busy table | Blocks writes for the whole build | `CREATE INDEX CONCURRENTLY` in its own file |
| `CONCURRENTLY ... IF NOT EXISTS` as a retry | Keeps the INVALID index from the failed build | Check `indisvalid`, drop, and rebuild |
| Backfill inside a migration | One long transaction, or `COMMIT` errors | Keyset-batched script through `psql` |
| Backfill before dual-write | Misses rows written in between | Dual-write deploy first, then backfill |
| Editing a migration that already ran | Environments drift | New forward migration |
| Policies created only in the dashboard | Not reproducible; lost on reset | Capture with `supabase db diff -f` |

## Sources

Checked 2026-10-26.

- PostgreSQL 18, ALTER TABLE (lock levels, ADD COLUMN defaults, SET NOT NULL scan skip, NOT VALID for CHECK and not-null constraints, DROP COLUMN): https://www.postgresql.org/docs/18/sql-altertable.html
- PostgreSQL 18, explicit locking (lock modes and conflicts): https://www.postgresql.org/docs/18/explicit-locking.html
- PostgreSQL 18, CREATE INDEX (CONCURRENTLY, invalid indexes, recovery): https://www.postgresql.org/docs/18/sql-createindex.html
- PostgreSQL 18, DROP INDEX (CONCURRENTLY caveats): https://www.postgresql.org/docs/18/sql-dropindex.html
- PostgreSQL, pg_index catalog (`indisvalid`): https://www.postgresql.org/docs/18/catalog-pg-index.html
- PostgreSQL, client settings (`lock_timeout`): https://www.postgresql.org/docs/current/runtime-config-client.html
- PostgreSQL, DO and PL/pgSQL transaction control: https://www.postgresql.org/docs/current/sql-do.html, https://www.postgresql.org/docs/18/plpgsql-transactions.html
- PostgreSQL, PL/pgSQL `SELECT INTO` with no rows and `%TYPE`: https://www.postgresql.org/docs/18/plpgsql-statements.html, https://www.postgresql.org/docs/18/plpgsql-declarations.html
- PostgreSQL, frontend protocol (multi-statement implicit transaction): https://www.postgresql.org/docs/current/protocol-flow.html
- PostgreSQL 18, psql (`-f`, `-v`, `ON_ERROR_STOP`, `AUTOCOMMIT`, `-1`): https://www.postgresql.org/docs/18/app-psql.html
- Lock queue behind a waiting ALTER TABLE: https://www.depesz.com/?p=3687
- Supabase CLI reference (`migration new`, `db diff`, `db push --dry-run`, `db reset`, `migration list`): https://supabase.com/docs/reference/cli/supabase-migration-new, https://supabase.com/docs/reference/cli/supabase-db-diff
- Supabase database migrations guide: https://supabase.com/docs/guides/deployment/database-migrations
- Supabase Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase CLI CONCURRENTLY handling: https://github.com/supabase/cli/commit/3eaee310bf40 and https://github.com/supabase/cli/commit/dc97151e51ec (apps/cli-go/pkg/migration/file.go)
- Prisma CLI reference (v7): https://www.prisma.io/docs/orm/reference/prisma-cli-reference
- Prisma CONCURRENTLY support (milestone 7.4.0): https://github.com/prisma/prisma-engines/pull/5767
- Drizzle Kit: https://orm.drizzle.team/docs/kit-overview, https://orm.drizzle.team/docs/kit-custom-migrations, https://orm.drizzle.team/docs/drizzle-kit-migrate
- Drizzle migrator transaction: https://github.com/drizzle-team/drizzle-orm/blob/main/drizzle-orm/src/pg-core/dialect.ts
- Alembic: https://alembic.sqlalchemy.org/en/latest/tutorial.html, https://alembic.sqlalchemy.org/en/latest/autogenerate.html, https://alembic.sqlalchemy.org/en/latest/api/runtime.html, https://alembic.sqlalchemy.org/en/latest/ops.html
- SQLAlchemy PostgreSQL dialect (`postgresql_concurrently`): https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
- golang-migrate: https://github.com/golang-migrate/migrate/blob/master/cmd/migrate/README.md, https://github.com/golang-migrate/migrate/blob/master/database/postgres/README.md

## Provenance

Adapted from the `database-migrations` skill in everything-claude-code (MIT). See `NOTICE.md` and `LICENSE.txt`.
