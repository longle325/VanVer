import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from services.knowledge_retriever import KnowledgeRetriever


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


class KnowledgeRetrieverTests(unittest.TestCase):
    def test_search_filters_by_character_slug(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "chunks.jsonl"
            write_jsonl(
                index_path,
                [
                    {
                        "chunk_id": "chi.chunk_1",
                        "character_slug": "chi_pheo",
                        "doc_type": "original",
                        "source_path": "Chi_Pheo/Chí_Phèo.txt",
                        "text": "Bát cháo hành của Thị Nở làm Chí Phèo muốn lương thiện.",
                    },
                    {
                        "chunk_id": "mi.chunk_1",
                        "character_slug": "mi",
                        "doc_type": "original",
                        "source_path": "Mi/Vợ_chồng_a_phủ.txt",
                        "text": "Tiếng sáo mùa xuân đánh thức Mị.",
                    },
                ],
            )

            retriever = KnowledgeRetriever(index_path=index_path)
            context = retriever.search_context("chi_pheo", "bát cháo hành")

            self.assertIn("Bát cháo hành", context)
            self.assertIn("Chi_Pheo/Chí_Phèo.txt", context)
            self.assertNotIn("Tiếng sáo", context)

    def test_search_returns_empty_string_when_no_terms_match(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "chunks.jsonl"
            write_jsonl(
                index_path,
                [
                    {
                        "chunk_id": "chi.chunk_1",
                        "character_slug": "chi_pheo",
                        "doc_type": "analysis",
                        "source_path": "Chi_Pheo/analysis.txt",
                        "text": "Bát cháo hành đánh thức phần người.",
                    }
                ],
            )

            retriever = KnowledgeRetriever(index_path=index_path)

            self.assertEqual(retriever.search_context("chi_pheo", "tennis"), "")

    def test_vector_literal_formats_float_array_for_pgvector(self):
        retriever = KnowledgeRetriever()

        self.assertEqual(retriever._vector_literal([0.1, 0.2, 0.3]), "[0.1,0.2,0.3]")

    def test_async_search_falls_back_to_lexical_context_when_vector_fails(self):
        class FailingVectorRetriever(KnowledgeRetriever):
            async def _search_vector_chunks(self, character_slug, user_query):
                raise RuntimeError("vector unavailable")

        async def run_search():
            with tempfile.TemporaryDirectory() as temp_dir:
                index_path = Path(temp_dir) / "chunks.jsonl"
                write_jsonl(
                    index_path,
                    [
                        {
                            "chunk_id": "chi.chunk_1",
                            "character_slug": "chi_pheo",
                            "doc_type": "original",
                            "source_path": "Chi_Pheo/Chí_Phèo.txt",
                            "text": "Bát cháo hành làm Chí Phèo muốn trở lại làm người.",
                        }
                    ],
                )
                retriever = FailingVectorRetriever(index_path=index_path)
                return await retriever.search_context_async("chi_pheo", "cháo hành")

        context = __import__("asyncio").run(run_search())

        self.assertIn("Bát cháo hành", context)

    def test_search_with_sources_returns_structured_lexical_citations(self):
        class FailingVectorRetriever(KnowledgeRetriever):
            async def _search_vector_chunks(self, character_slug, user_query):
                raise RuntimeError("vector unavailable")

        async def run_search():
            with tempfile.TemporaryDirectory() as temp_dir:
                index_path = Path(temp_dir) / "chunks.jsonl"
                write_jsonl(
                    index_path,
                    [
                        {
                            "chunk_id": "chi.chunk_1",
                            "document_id": "chi.doc",
                            "character_slug": "chi_pheo",
                            "character_name": "Chí Phèo",
                            "doc_type": "analysis",
                            "source_path": "Chi_Pheo/analysis.txt",
                            "text": "Bát cháo hành đánh thức phần người.",
                        }
                    ],
                )
                retriever = FailingVectorRetriever(index_path=index_path)
                return await retriever.search_with_sources_async("chi_pheo", "bát cháo")

        result = __import__("asyncio").run(run_search())

        self.assertEqual(result["retrieval_mode"], "lexical")
        self.assertIn("Bát cháo hành", result["context"])
        self.assertEqual(result["sources"][0]["chunk_id"], "chi.chunk_1")
        self.assertEqual(result["sources"][0]["source_path"], "Chi_Pheo/analysis.txt")

    def test_diagnostics_reports_lexical_fallback_availability(self):
        class FailingSessionFactory:
            def __call__(self):
                return self

            async def __aenter__(self):
                raise RuntimeError("database unavailable")

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        async def run_diagnostics():
            with tempfile.TemporaryDirectory() as temp_dir:
                index_path = Path(temp_dir) / "chunks.jsonl"
                write_jsonl(
                    index_path,
                    [
                        {
                            "chunk_id": "chi.chunk_1",
                            "document_id": "chi.doc",
                            "character_slug": "chi_pheo",
                            "source_path": "source.txt",
                            "doc_type": "analysis",
                            "text": "context",
                        }
                    ],
                )
                with patch(
                    "services.knowledge_retriever.async_session_factory",
                    FailingSessionFactory(),
                ):
                    return await KnowledgeRetriever(index_path=index_path).diagnostics()

        result = __import__("asyncio").run(run_diagnostics())

        self.assertEqual(result["lexical_chunk_count"], 1)
        self.assertTrue(result["fallback_available"])
        self.assertEqual(result["embedding_model"], "text-embedding-3-large")


if __name__ == "__main__":
    unittest.main()
