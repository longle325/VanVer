# Runbook: bring the existing prod DB under Alembic control

**Run this ONCE, against production, BEFORE merging the change that adds
`alembic upgrade head` to the deploy pipeline.** If you skip it, the first
post-merge deploy fails: the prod DB was built by `create_all` and has **no
`alembic_version` table**, so a bare `alembic upgrade head` tries to re-create
tables that already exist.

Goal: make the live schema match what `alembic upgrade head` produces, then
`alembic stamp` the DB so Alembic knows it is already at that revision. After
that, every deploy's `alembic upgrade head` applies only genuinely-new
migrations.

Requires: the production `DATABASE_URL` and `psql` access to the prod DB. Do it
from a machine that can reach the DB (or a GitHub Actions one-off), with the
backend deps installed (`pip install -r backend/requirements.txt`).

---

## 0. Back up first (non-negotiable)

```bash
pg_dump "$PROD_DATABASE_URL_PSQL" > vanver-prod-$(date +%Y%m%d-%H%M%S).sql
```

> Note: Alembic/the app use the `postgresql+asyncpg://` URL; `pg_dump`/`psql`
> want a plain `postgresql://` URL (drop `+asyncpg`).

## 1. Confirm it is not already under Alembic

```sql
SELECT to_regclass('public.alembic_version');   -- expect NULL (not yet stamped)
```

If this returns `alembic_version`, the DB is already stamped — run
`alembic current` and skip to step 4.

## 2. Inspect the live schema to find the matching revision

The migrations build, in order: `0001` core tables → `0002` relationship/event
tables → `0003` OAuth columns on `users` → `0004` `user_progress` table.

Check what prod actually has:

```sql
-- 0003: OAuth columns on users
SELECT column_name FROM information_schema.columns
WHERE table_name = 'users'
  AND column_name IN ('email','display_name','auth_provider','auth_subject','last_login_at');

-- 0004: user_progress table
SELECT to_regclass('public.user_progress');

-- 0002: graph tables
SELECT to_regclass('public.character_relationships'), to_regclass('public.character_events');
```

Because `create_all` creates missing **tables** but never **alters** existing
ones, prod can be in a *mixed* state (e.g. `user_progress` present but the OAuth
columns on `users` missing) that matches **no single revision**. That is normal
and expected here — handle it in step 3.

## 3. Reconcile the live schema to `head`

Make the live schema equal to what `alembic upgrade head` would produce, by
hand-applying only the pieces that are missing.

If the OAuth columns from step 2 are **missing**, apply migration `0003`'s DDL
(idempotent form):

```sql
BEGIN;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email         varchar(320);
ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name  varchar(120);
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider varchar(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_subject  varchar(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at timestamptz;
CREATE INDEX IF NOT EXISTS ix_users_email         ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_auth_provider ON users (auth_provider);
-- add the unique constraint only if it isn't there yet
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_users_auth_provider_subject') THEN
    ALTER TABLE users ADD CONSTRAINT uq_users_auth_provider_subject UNIQUE (auth_provider, auth_subject);
  END IF;
END $$;
COMMIT;
```

If `user_progress` (0004) or the graph tables (0002) are missing, create them to
match the model — easiest is to let the app's old `create_all` path (or a manual
`CREATE TABLE` copied from the migration) add only those missing tables, since
`create_all` never touches the tables that already exist.

After this step, the live schema should be identical to a fresh
`alembic upgrade head` schema.

## 4. Stamp the DB at `head`

```bash
cd backend
DATABASE_URL="$PROD_DATABASE_URL" alembic -c alembic.ini stamp head
```

This writes `alembic_version = 0004_add_user_progress` (the current head)
**without running any DDL** — it just records that prod is already at that state.

## 5. Verify

```bash
cd backend
DATABASE_URL="$PROD_DATABASE_URL" alembic -c alembic.ini current      # -> 0004_add_user_progress (head)
DATABASE_URL="$PROD_DATABASE_URL" alembic -c alembic.ini upgrade head # -> no-op, no errors
```

```sql
SELECT version_num FROM alembic_version;   -- 0004_add_user_progress
```

If `upgrade head` is a clean no-op, prod is now under Alembic control.

## 6. Then ship

Merge the PR that removes `create_all` and adds the `alembic upgrade head` deploy
step. From now on each deploy runs migrations before the new revision serves
traffic, and the CI gate (`.github/workflows/migrations.yml`) proves the
migrations still apply to an empty DB on every PR.

---

### If something goes wrong

Restore from the step-0 dump:

```bash
psql "$PROD_DATABASE_URL_PSQL" < vanver-prod-<timestamp>.sql
```

`alembic stamp` only writes the version table, so the main risk is in step 3
(hand-applied DDL) — which is why step 0 exists.
