#!/usr/bin/env bash
#
# Dump the embedded `knowledge_chunks` table to a portable, gzipped SQL
# file so teammates can restore the RAG vector store without re-running
# `embed_knowledge_base.py` (which costs OpenAI tokens and ~5–10 minutes
# per run).
#
# Run this AFTER `backend/scripts/embed_knowledge_base.py` has populated
# the table — typically after you've added or modified chunks in
# backend/knowledge_base/index/chunks.jsonl.
#
# Usage (from the repo root):
#   bash scripts/dump-knowledge-chunks.sh
#
# Output: backend/data/knowledge_chunks.sql.gz
#
# After dumping, commit the artifact (or upload it to team storage and
# bump scripts/restore-knowledge-chunks.sh's DUMP_URL accordingly).

set -euo pipefail

CONTAINER="${VANVER_PG_CONTAINER:-vanver-postgres}"
DB="${VANVER_PG_DB:-vanver}"
PGUSER_NAME="${VANVER_PG_USER:-postgres}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO_ROOT/backend/data/knowledge_chunks.sql.gz"

mkdir -p "$(dirname "$OUT")"

if ! docker exec "$CONTAINER" pg_isready -U "$PGUSER_NAME" -d "$DB" >/dev/null 2>&1; then
  echo "ERR: postgres container '$CONTAINER' is not ready. Did you run 'docker compose up -d postgres'?" >&2
  exit 1
fi

ROWS=$(docker exec -i "$CONTAINER" psql -U "$PGUSER_NAME" -d "$DB" -tAc "SELECT count(*) FROM knowledge_chunks;" 2>/dev/null || echo "0")
if [ "$ROWS" -eq 0 ]; then
  echo "ERR: knowledge_chunks is empty. Run 'backend/.venv/bin/python scripts/embed_knowledge_base.py --batch-size 24' first." >&2
  exit 1
fi

echo "Dumping $ROWS chunks from $CONTAINER:$DB ..."

docker exec -i "$CONTAINER" pg_dump \
  -U "$PGUSER_NAME" \
  -d "$DB" \
  --data-only \
  --column-inserts \
  --no-owner \
  --table=knowledge_chunks \
  | gzip -9 > "$OUT"

SIZE_HUMAN=$(du -h "$OUT" | cut -f1)
SIZE_BYTES=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT")

echo "Wrote $OUT ($SIZE_HUMAN, $SIZE_BYTES bytes, $ROWS rows)"
echo
echo "Next steps:"
echo "  1. Commit the artifact:    git add $OUT && git commit -m 'Refresh knowledge_chunks dump'"
echo "  2. Or upload externally:   stash to team Drive and update DUMP_URL in scripts/restore-knowledge-chunks.sh"
