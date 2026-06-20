import unittest
from types import SimpleNamespace

from services.chat_service import ChatService


class ChatServiceCompletionOptionsTests(unittest.TestCase):
    def test_gpt_5_models_use_max_completion_tokens(self):
        service = ChatService(
            codex_agent=None,
            openai_client=object(),
            chat_model="gpt-5.1",
        )

        kwargs = service._completion_kwargs("system", "message")

        self.assertEqual(kwargs["max_completion_tokens"], 1024)
        self.assertNotIn("max_tokens", kwargs)
        self.assertNotIn("temperature", kwargs)

    def test_legacy_chat_models_use_max_tokens(self):
        service = ChatService(
            codex_agent=None,
            openai_client=object(),
            chat_model="gpt-4o",
        )

        kwargs = service._completion_kwargs("system", "message")

        self.assertEqual(kwargs["max_tokens"], 1024)
        self.assertEqual(kwargs["temperature"], 0.7)
        self.assertNotIn("max_completion_tokens", kwargs)

    def test_stream_response_uses_async_hybrid_retriever_context(self):
        class FakeRetriever:
            def __init__(self):
                self.called = False

            async def search_context_async(self, character_slug, user_query):
                self.called = True
                self.character_slug = character_slug
                self.user_query = user_query
                return "VECTOR_CONTEXT_FROM_PGVECTOR"

        class FakeCompletions:
            def __init__(self):
                self.kwargs = None

            async def create(self, **kwargs):
                self.kwargs = kwargs

                async def stream():
                    yield SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                delta=SimpleNamespace(content="xin chào")
                            )
                        ]
                    )

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.chat = SimpleNamespace(completions=FakeCompletions())

        async def collect_response():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-4o",
            )

            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="chi_pheo",
                    character_name="Chí Phèo",
                    user_message="bát cháo hành là gì?",
                )
            ]
            return retriever, client, chunks

        retriever, client, chunks = __import__("asyncio").run(collect_response())
        system_prompt = client.chat.completions.kwargs["messages"][0]["content"]

        self.assertTrue(retriever.called)
        self.assertEqual(retriever.character_slug, "chi_pheo")
        self.assertIn("VECTOR_CONTEXT_FROM_PGVECTOR", system_prompt)
        self.assertEqual(chunks, ["xin chào"])

    def test_stream_response_includes_recent_chat_history_in_prompt(self):
        class FakeCompletions:
            def __init__(self):
                self.kwargs = None

            async def create(self, **kwargs):
                self.kwargs = kwargs

                async def stream():
                    yield SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                delta=SimpleNamespace(content="tôi nhớ")
                            )
                        ]
                    )

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.chat = SimpleNamespace(completions=FakeCompletions())

        async def collect_prompt():
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=None,
                openai_client=client,
                chat_model="gpt-4o",
            )
            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="mi",
                    character_name="Mị",
                    user_message="Còn sau đó thì sao?",
                    chat_history=[
                        {"role": "user", "content": "Trước đó em hỏi về tiếng sáo."},
                        {"role": "assistant", "content": "Ta đã nghe tiếng sáo gọi về tuổi trẻ."},
                    ],
                )
            ]
            return client.chat.completions.kwargs["messages"][0]["content"], chunks

        system_prompt, chunks = __import__("asyncio").run(collect_prompt())

        self.assertIn("[RECENT CONVERSATION HISTORY]", system_prompt)
        self.assertIn("Student: Trước đó em hỏi về tiếng sáo.", system_prompt)
        self.assertIn("Character: Ta đã nghe tiếng sáo gọi về tuổi trẻ.", system_prompt)
        self.assertEqual(chunks, ["tôi nhớ"])

    def test_format_chat_history_limits_prompt_context(self):
        history = [
            {"role": "user", "content": f"old message {index}"}
            for index in range(6)
        ]
        history.extend(
            [
                {
                    "role": "assistant",
                    "content": "assistant says " + ("x" * 80),
                },
                {
                    "role": "user",
                    "content": "latest user asks about the next moment",
                },
            ]
        )

        formatted = ChatService._format_chat_history(
            history,
            max_messages=3,
            max_chars_per_message=32,
            max_total_chars=140,
        )

        self.assertLessEqual(len(formatted), 140)
        self.assertNotIn("old message 0", formatted)
        self.assertNotIn("old message 4", formatted)
        self.assertIn("Student: latest user asks about", formatted)
        self.assertIn("... [truncated]", formatted)

    def test_prepare_retrieval_returns_sources_for_frontend(self):
        class FakeRetriever:
            async def search_with_sources_async(self, character_slug, user_query):
                return {
                    "context": "context",
                    "retrieval_mode": "vector",
                    "sources": [{"chunk_id": "chunk_1", "source_path": "source.txt"}],
                }

        async def prepare():
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=FakeRetriever(),
                openai_client=object(),
            )
            return await service.prepare_retrieval(
                character_slug="chi_pheo",
                character_name="Chí Phèo",
                user_message="bát cháo",
            )

        result = __import__("asyncio").run(prepare())

        self.assertEqual(result["retrieval_mode"], "vector")
        self.assertEqual(result["sources"][0]["chunk_id"], "chunk_1")


if __name__ == "__main__":
    unittest.main()
