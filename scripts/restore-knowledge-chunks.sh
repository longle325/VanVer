#!/usr/bin/env bash
#
# Restore the embedded `knowledge_chunks` table from a portable SQL dump
# so a fresh teammate gets working RAG retrieval without spending OpenAI
# tokens on the embed script.
#
# Usage (from the repo root, AFTER `seed_database.py` has run so the
# table schema exists):
#
#   bash scripts/restore-knowledge-chunks.sh                 # uses backend/data/knowledge_chunks.sql.gz
#   DUMP_URL=https://… bash scripts/restore-knowledge-chunks.sh   # downloads first
#
# The script truncates `knowledge_chunks` before loading, so re-runs are
# idempotent and any stale rows from a previous embedding pass get
# evicted.

set -euo pipefail

CONTAINER="${VANVER_PG_CONTAINER:-vanver-postgres}"
DB="${VANVER_PG_DB:-vanver}"
PGUSER_NAME="${VANVER_PG_USER:-postgres}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DUMP="$REPO_ROOT/backend/data/knowledge_chunks.sql.gz"

# Default to the team's Google Drive copy (gzipped pg_dump of the
# knowledge_chunks table). Override with `DUMP_URL=...` if you've moved it.
DEFAULT_DUMP_URL="https://drive.google.com/uc?export=download&id=1cGlRIXH9EOJEwfb22USsUhSV6NCAcq_D"
DUMP_URL="${DUMP_URL:-$DEFAULT_DUMP_URL}"

if [ ! -f "$DUMP" ] && [ -n "$DUMP_URL" ]; then
  echo "Downloading dump from $DUMP_URL ..."
  mkdir -p "$(dirname "$DUMP")"
  curl -fsSL --retry 3 -o "$DUMP" "$DUMP_URL"
fi

if [ ! -f "$DUMP" ]; then
  cat >&2 <<EOF
ERR: dump not found: $DUMP

Options to obtain it:
  - Run 'bash scripts/dump-knowledge-chunks.sh' on a workspace that has
    already embedded the knowledge base.
  - Or set DUMP_URL=<team-drive-link> when running this script.
  - Or fall back to embedding from scratch (costs OpenAI tokens):
      cd backend && ./.venv/bin/python scripts/embed_knowledge_base.py --batch-size 24
EOF
  exit 1
fi

if ! docker exec "$CONTAINER" pg_isready -U "$PGUSER_NAME" -d "$DB" >/dev/null 2>&1; then
  echo "ERR: postgres container '$CONTAINER' is not ready. Run 'docker compose up -d postgres'." >&2
  exit 1
fi

# Make sure the schema exists. The lifespan/seed scripts create it; if
# someone runs restore before seed, fail loudly with a clear hint.
if ! docker exec -i "$CONTAINER" psql -U "$PGUSER_NAME" -d "$DB" -tAc "SELECT to_regclass('public.knowledge_chunks');" | grep -q knowledge_chunks; then
  echo "ERR: 'knowledge_chunks' table doesn't exist yet." >&2
  echo "Run 'cd backend && ./.venv/bin/python scripts/seed_database.py' first." >&2
  exit 1
fi

echo "Truncating existing chunks ..."
docker exec -i "$CONTAINER" psql -U "$PGUSER_NAME" -d "$DB" -v ON_ERROR_STOP=1 \
  -c "TRUNCATE knowledge_chunks RESTART IDENTITY CASCADE;" >/dev/null

echo "Loading $(du -h "$DUMP" | cut -f1) of dump into $CONTAINER:$DB ..."
gunzip -c "$DUMP" | docker exec -i "$CONTAINER" psql -U "$PGUSER_NAME" -d "$DB" -v ON_ERROR_STOP=1 -q

ROWS=$(docker exec -i "$CONTAINER" psql -U "$PGUSER_NAME" -d "$DB" -tAc "SELECT count(*) FROM knowledge_chunks;")
echo "Restored $ROWS chunks."
