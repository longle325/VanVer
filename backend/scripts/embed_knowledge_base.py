from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.config import settings  # noqa: E402
from core.database import Base, async_session_factory, engine, ensure_vector_extension  # noqa: E402
from models.db_models import KnowledgeChunk  # noqa: E402


DEFAULT_BATCH_SIZE = 64


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def batched[T](items: Sequence[T], batch_size: int) -> Iterable[list[T]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")
    for index in range(0, len(items), batch_size):
        yield list(items[index : index + batch_size])


def load_chunks(path: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def build_embedding_record(
    chunk: dict[str, Any],
    embedding: list[float],
    embedding_model: str,
) -> dict[str, Any]:
    return {
        "chunk_id": chunk["chunk_id"],
        "document_id": chunk["document_id"],
        "character_slug": chunk["character_slug"],
        "character_name": chunk["character_name"],
        "work_title": chunk.get("work_title"),
        "author": chunk.get("author"),
        "doc_type": chunk["doc_type"],
        "source_path": chunk["source_path"],
        "text_hash": text_hash(chunk["text"]),
        "text": chunk["text"],
        "embedding_model": embedding_model,
        "embedding": embedding,
    }


class OpenAIEmbeddingClient:
    def __init__(
        self,
        api_key: str,
        model: str,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]


async def existing_hashes() -> dict[str, str]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(KnowledgeChunk.chunk_id, KnowledgeChunk.text_hash).where(
                KnowledgeChunk.embedding_model == settings.EMBEDDING_MODEL
            )
        )
        return {chunk_id: hash_value for chunk_id, hash_value in result.all()}


async def upsert_records(records: list[dict[str, Any]]) -> None:
    if not records:
        return

    stmt = insert(KnowledgeChunk).values(records)
    excluded = stmt.excluded
    update_values = {
        "document_id": excluded.document_id,
        "character_slug": excluded.character_slug,
        "character_name": excluded.character_name,
        "work_title": excluded.work_title,
        "author": excluded.author,
        "doc_type": excluded.doc_type,
        "source_path": excluded.source_path,
        "text_hash": excluded.text_hash,
        "text": excluded.text,
        "embedding_model": excluded.embedding_model,
        "embedding": excluded.embedding,
    }
    stmt = stmt.on_conflict_do_update(
        constraint="uq_knowledge_chunk_id",
        set_=update_values,
    )

    async with async_session_factory() as session:
        await session.execute(stmt)
        await session.commit()


async def embed_knowledge_base(
    chunks_path: Path,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict[str, int]:
    await ensure_vector_extension()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    chunks = load_chunks(chunks_path)
    hashes = await existing_hashes()
    pending = [
        chunk
        for chunk in chunks
        if hashes.get(chunk["chunk_id"]) != text_hash(chunk["text"])
    ]
    skipped = len(chunks) - len(pending)

    embedding_client = OpenAIEmbeddingClient(
        api_key=settings.OPENAI_API_KEY,
        model=settings.EMBEDDING_MODEL,
    )

    embedded_count = 0
    for chunk_batch in batched(pending, batch_size):
        embeddings = await embedding_client.embed_texts(
            [chunk["text"] for chunk in chunk_batch]
        )
        records = [
            build_embedding_record(chunk, embedding, settings.EMBEDDING_MODEL)
            for chunk, embedding in zip(chunk_batch, embeddings)
        ]
        await upsert_records(records)
        embedded_count += len(records)
        print(f"Embedded {embedded_count}/{len(pending)} chunks...")

    await engine.dispose()
    return {
        "total": len(chunks),
        "embedded": embedded_count,
        "skipped": skipped,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed Vanver knowledge chunks.")
    parser.add_argument(
        "--chunks-path",
        type=Path,
        default=Path(settings.KNOWLEDGE_BASE_DIR) / "index" / "chunks.jsonl",
    )
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stats = asyncio.run(
        embed_knowledge_base(
            chunks_path=args.chunks_path,
            batch_size=args.batch_size,
        )
    )
    print(
        "Embedding complete: "
        f"total={stats['total']} embedded={stats['embedded']} skipped={stats['skipped']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
