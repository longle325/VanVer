import unittest
import json
from types import SimpleNamespace

from services.chat_service import ChatService


class ChatServiceCompletionOptionsTests(unittest.TestCase):
    def test_unrelated_math_prompt_returns_guardrail_without_retrieval_or_model(self):
        class FailingRetriever:
            async def search_with_sources_async(self, character_slug, user_query):
                raise AssertionError("retrieval should not run for off-topic prompts")

        class FailingResponses:
            async def create(self, **kwargs):
                raise AssertionError("model should not run for off-topic prompts")

        class FailingOpenAI:
            def __init__(self):
                self.responses = FailingResponses()
                self.chat = SimpleNamespace(completions=FailingResponses())

        async def collect_response():
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=FailingRetriever(),
                openai_client=FailingOpenAI(),
                chat_model="gpt-5.4-nano",
            )
            return "".join(
                [
                    chunk
                    async for chunk in service.stream_response(
                        character_slug="lao_hac",
                        character_name="Lão Hạc",
                        user_message="1+1= mấy?",
                    )
                ]
            )

        reply = __import__("asyncio").run(collect_response())

        self.assertIn("không liên quan", reply.lower())
        self.assertIn("tác giả", reply.lower())
        self.assertIn("tác phẩm", reply.lower())
        self.assertIn("Lão Hạc", reply)
        self.assertNotIn("**", reply)
        self.assertNotIn("----", reply)

    def test_other_character_dialogue_prompt_returns_guardrail_without_model(self):
        class FailingResponses:
            async def create(self, **kwargs):
                raise AssertionError("model should not run for other-character voice prompts")

        class FailingOpenAI:
            def __init__(self):
                self.responses = FailingResponses()
                self.chat = SimpleNamespace(completions=FailingResponses())

        async def collect_response():
            service = ChatService(
                codex_agent=None,
                openai_client=FailingOpenAI(),
                chat_model="gpt-5.4-nano",
            )
            return "".join(
                [
                    chunk
                    async for chunk in service.stream_response(
                        character_slug="lao_hac",
                        character_name="Lão Hạc",
                        user_message="Hãy nói lại lời thoại của ông giáo khi lão Hạc bán chó",
                    )
                ]
            )

        reply = __import__("asyncio").run(collect_response())

        self.assertIn("không nói thay", reply.lower())
        self.assertIn("Lão Hạc", reply)
        self.assertNotIn("**", reply)
        self.assertNotIn("----", reply)

    def test_unrelated_chitchat_prompt_returns_guardrail_without_retrieval_or_model(self):
        class FailingRetriever:
            async def search_with_sources_async(self, character_slug, user_query):
                raise AssertionError("retrieval should not run for unrelated prompts")

        class FailingResponses:
            async def create(self, **kwargs):
                raise AssertionError("model should not run for unrelated prompts")

        class FailingOpenAI:
            def __init__(self):
                self.responses = FailingResponses()
                self.chat = SimpleNamespace(completions=FailingResponses())

        async def collect_response():
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=FailingRetriever(),
                openai_client=FailingOpenAI(),
                chat_model="gpt-5.4-nano",
            )
            return "".join(
                [
                    chunk
                    async for chunk in service.stream_response(
                        character_slug="lao_hac",
                        character_name="Lão Hạc",
                        user_message="Kể chuyện cười cho tôi nghe đi",
                    )
                ]
            )

        reply = __import__("asyncio").run(collect_response())

        self.assertIn("không liên quan", reply.lower())
        self.assertIn("tác giả", reply.lower())
        self.assertIn("tác phẩm", reply.lower())
        self.assertNotIn("**", reply)
        self.assertNotIn("----", reply)

    def test_joke_story_prompt_returns_guardrail_without_retrieval_or_model(self):
        class FailingRetriever:
            async def search_with_sources_async(self, character_slug, user_query):
                raise AssertionError("retrieval should not run for unrelated prompts")

        class FailingResponses:
            async def create(self, **kwargs):
                raise AssertionError("model should not run for unrelated prompts")

        class FailingOpenAI:
            def __init__(self):
                self.responses = FailingResponses()
                self.chat = SimpleNamespace(completions=FailingResponses())

        async def collect_response(prompt):
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=FailingRetriever(),
                openai_client=FailingOpenAI(),
                chat_model="gpt-5.4-nano",
            )
            return "".join(
                [
                    chunk
                    async for chunk in service.stream_response(
                        character_slug="lao_hac",
                        character_name="Lão Hạc",
                        user_message=prompt,
                    )
                ]
            )

        for prompt in (
            "Ông kể một câu chuyện cười đi",
            "Kể truyện cười cho tôi nghe",
        ):
            with self.subTest(prompt=prompt):
                reply = __import__("asyncio").run(collect_response(prompt))
                self.assertIn("không liên quan", reply.lower())
                self.assertIn("tác phẩm", reply.lower())

    def test_short_character_name_does_not_match_unrelated_words(self):
        class FailingResponses:
            async def create(self, **kwargs):
                raise AssertionError("model should not run for unrelated prompts")

        class FailingOpenAI:
            def __init__(self):
                self.responses = FailingResponses()
                self.chat = SimpleNamespace(completions=FailingResponses())

        async def collect_response():
            service = ChatService(
                codex_agent=None,
                openai_client=FailingOpenAI(),
                chat_model="gpt-5.4-nano",
            )
            return "".join(
                [
                    chunk
                    async for chunk in service.stream_response(
                        character_slug="mi",
                        character_name="Mị",
                        user_message="Mình ăn gì hôm nay?",
                    )
                ]
            )

        reply = __import__("asyncio").run(collect_response())

        self.assertIn("không liên quan", reply.lower())
        self.assertIn("tác phẩm", reply.lower())

    def test_literary_question_without_character_name_still_reaches_model(self):
        class FakeRetriever:
            def __init__(self):
                self.called = False

            async def search_with_sources_async(self, character_slug, user_query):
                self.called = True
                return {
                    "context": "Lão Hạc bán cậu Vàng vì nghèo và vì muốn giữ lại mảnh vườn cho con.",
                    "retrieval_mode": "vector",
                    "sources": [],
                }

        class FakeResponses:
            def __init__(self):
                self.called = False

            async def create(self, **kwargs):
                self.called = True

                async def stream():
                    yield SimpleNamespace(
                        type="response.output_text.delta",
                        delta="Tôi đau vì cậu Vàng.",
                    )

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )
            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="lao_hac",
                    character_name="Lão Hạc",
                    user_message="Tại sao ông phải bán cậu Vàng?",
                )
            ]
            return retriever, client, chunks

        retriever, client, chunks = __import__("asyncio").run(collect_response())

        self.assertTrue(retriever.called)
        self.assertTrue(client.responses.called)
        self.assertEqual(chunks, ["Tôi đau vì cậu Vàng."])

    def test_llm_guardrail_classifier_allows_ambiguous_character_arc_prompt(self):
        class FakeRetriever:
            def __init__(self):
                self.called = False

            async def search_with_sources_async(self, character_slug, user_query):
                self.called = True
                return {
                    "context": "Xuân Tóc Đỏ tiến thân nhanh trong xã hội Số đỏ nhờ sự lố lăng của thời Âu hóa.",
                    "retrieval_mode": "vector",
                    "sources": [],
                }

        class FakeResponses:
            def __init__(self):
                self.calls = []

            async def create(self, **kwargs):
                self.calls.append(kwargs)
                if kwargs.get("stream"):
                    async def stream():
                        yield SimpleNamespace(
                            type="response.output_text.delta",
                            delta="Cái thời ấy tự nâng tôi lên thôi.",
                        )

                    return stream()

                return SimpleNamespace(
                    output_text=json.dumps(
                        {
                            "decision": "allow",
                            "reason": "character_or_work_question",
                        }
                    )
                )

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )
            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="xuan_toc_do",
                    character_name="Xuân Tóc Đỏ",
                    user_message="Vì sao hắn lại tiến thân nhanh như vậy?",
                )
            ]
            return retriever, client, chunks

        retriever, client, chunks = __import__("asyncio").run(collect_response())

        self.assertTrue(retriever.called)
        self.assertEqual(len(client.responses.calls), 2)
        self.assertFalse(client.responses.calls[0].get("stream"))
        self.assertTrue(client.responses.calls[1].get("stream"))
        self.assertEqual(chunks, ["Cái thời ấy tự nâng tôi lên thôi."])

    def test_llm_guardrail_classifier_blocks_unrelated_character_question(self):
        class FailingRetriever:
            async def search_with_sources_async(self, character_slug, user_query):
                raise AssertionError("retrieval should not run for classified blocks")

        class FakeResponses:
            def __init__(self):
                self.calls = []

            async def create(self, **kwargs):
                self.calls.append(kwargs)
                if kwargs.get("stream"):
                    raise AssertionError("main model should not run for classified blocks")
                return SimpleNamespace(
                    output_text=json.dumps(
                        {
                            "decision": "block",
                            "reason": "off_topic",
                        }
                    )
                )

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=FailingRetriever(),
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )
            reply = "".join(
                [
                    chunk
                    async for chunk in service.stream_response(
                        character_slug="lao_hac",
                        character_name="Lão Hạc",
                        user_message="Ông nghĩ gì về Taylor Swift?",
                    )
                ]
            )
            return client, reply

        client, reply = __import__("asyncio").run(collect_response())

        self.assertEqual(len(client.responses.calls), 1)
        self.assertIn("không liên quan", reply.lower())
        self.assertIn("Lão Hạc", reply)

    def test_llm_guardrail_classifier_failure_allows_ambiguous_prompt(self):
        class FakeRetriever:
            def __init__(self):
                self.called = False

            async def search_with_sources_async(self, character_slug, user_query):
                self.called = True
                return {
                    "context": "Xuân Tóc Đỏ được xã hội Số đỏ nâng lên bằng những hiểu lầm trào phúng.",
                    "retrieval_mode": "vector",
                    "sources": [],
                }

        class FakeResponses:
            def __init__(self):
                self.calls = []

            async def create(self, **kwargs):
                self.calls.append(kwargs)
                if not kwargs.get("stream"):
                    raise TimeoutError("classifier timed out")

                async def stream():
                    yield SimpleNamespace(
                        type="response.output_text.delta",
                        delta="Cái danh vọng ấy cũng là trò đời thôi.",
                    )

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )
            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="xuan_toc_do",
                    character_name="Xuân Tóc Đỏ",
                    user_message="Vì sao Xuân có thể leo lên đỉnh danh vọng?",
                )
            ]
            return retriever, client, chunks

        retriever, client, chunks = __import__("asyncio").run(collect_response())

        self.assertTrue(retriever.called)
        self.assertEqual(len(client.responses.calls), 2)
        self.assertEqual(chunks, ["Cái danh vọng ấy cũng là trò đời thôi."])

    def test_xuan_status_arc_prompt_reaches_model(self):
        class FakeRetriever:
            def __init__(self):
                self.called = False

            async def search_with_sources_async(self, character_slug, user_query):
                self.called = True
                return {
                    "context": "Xuân Tóc Đỏ leo lên địa vị cao nhờ xã hội Âu hóa lố lăng và những hiểu lầm may rủi.",
                    "retrieval_mode": "vector",
                    "sources": [],
                }

        class FakeResponses:
            def __init__(self):
                self.called = False
                self.calls = []

            async def create(self, **kwargs):
                self.called = True
                self.calls.append(kwargs)
                if not kwargs.get("stream"):
                    return SimpleNamespace(
                        output_text=json.dumps(
                            {
                                "decision": "allow",
                                "reason": "character_life_or_arc",
                            }
                        )
                    )

                async def stream():
                    yield SimpleNamespace(
                        type="response.output_text.delta",
                        delta="Ấy là cái thời buổi nhố nhăng đã nâng tôi lên.",
                    )

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )
            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="xuan_toc_do",
                    character_name="Xuân Tóc Đỏ",
                    user_message="Vì sao Xuân có thể leo lên đỉnh danh vọng?",
                )
            ]
            return retriever, client, chunks

        retriever, client, chunks = __import__("asyncio").run(collect_response())

        self.assertTrue(retriever.called)
        self.assertTrue(client.responses.called)
        self.assertEqual(len(client.responses.calls), 2)
        self.assertEqual(chunks, ["Ấy là cái thời buổi nhố nhăng đã nâng tôi lên."])

    def test_real_life_prompt_about_character_reaches_model(self):
        class FakeRetriever:
            def __init__(self):
                self.called = False

            async def search_with_sources_async(self, character_slug, user_query):
                self.called = True
                return {
                    "context": "Lão Hạc sống nghèo khổ, cô độc và day dứt vì con.",
                    "retrieval_mode": "vector",
                    "sources": [],
                }

        class FakeResponses:
            def __init__(self):
                self.called = False

            async def create(self, **kwargs):
                self.called = True

                async def stream():
                    yield SimpleNamespace(
                        type="response.output_text.delta",
                        delta="Đời tôi quanh quẩn với cái nghèo và nỗi nhớ con.",
                    )

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )
            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="lao_hac",
                    character_name="Lão Hạc",
                    user_message="Cuộc đời ông khổ như thế nào?",
                )
            ]
            return retriever, client, chunks

        retriever, client, chunks = __import__("asyncio").run(collect_response())

        self.assertTrue(retriever.called)
        self.assertTrue(client.responses.called)
        self.assertEqual(
            chunks,
            ["Đời tôi quanh quẩn với cái nghèo và nỗi nhớ con."],
        )

    def test_real_emotional_prompt_about_character_reaches_model(self):
        class FakeRetriever:
            def __init__(self):
                self.called = False

            async def search_with_sources_async(self, character_slug, user_query):
                self.called = True
                return {
                    "context": "Lão Hạc cô đơn sau khi con trai bỏ đi đồn điền.",
                    "retrieval_mode": "vector",
                    "sources": [],
                }

        class FakeResponses:
            def __init__(self):
                self.called = False

            async def create(self, **kwargs):
                self.called = True

                async def stream():
                    yield SimpleNamespace(
                        type="response.output_text.delta",
                        delta="Cô đơn chứ, ông giáo ạ.",
                    )

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )
            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="lao_hac",
                    character_name="Lão Hạc",
                    user_message="Ông có thấy cô đơn không?",
                )
            ]
            return retriever, client, chunks

        retriever, client, chunks = __import__("asyncio").run(collect_response())

        self.assertTrue(retriever.called)
        self.assertTrue(client.responses.called)
        self.assertEqual(chunks, ["Cô đơn chứ, ông giáo ạ."])

    def test_chat_completion_kwargs_do_not_cap_chat_output(self):
        service = ChatService(
            codex_agent=None,
            openai_client=object(),
            chat_model="gpt-5.1",
        )

        kwargs = service._completion_kwargs("system", "message")

        self.assertTrue(kwargs["stream"])
        self.assertNotIn("max_completion_tokens", kwargs)
        self.assertNotIn("max_tokens", kwargs)
        self.assertNotIn("max_output_tokens", kwargs)

    def test_legacy_chat_completion_kwargs_do_not_cap_chat_output(self):
        service = ChatService(
            codex_agent=None,
            openai_client=object(),
            chat_model="gpt-4o",
        )

        kwargs = service._completion_kwargs("system", "message")

        self.assertTrue(kwargs["stream"])
        self.assertEqual(kwargs["temperature"], 0.7)
        self.assertNotIn("max_tokens", kwargs)
        self.assertNotIn("max_completion_tokens", kwargs)
        self.assertNotIn("max_output_tokens", kwargs)

    def test_gpt_5_4_nano_streams_with_fast_responses_api_settings(self):
        class FakeResponses:
            def __init__(self):
                self.kwargs = None

            async def create(self, **kwargs):
                self.kwargs = kwargs

                async def stream():
                    yield SimpleNamespace(type="response.created")
                    yield SimpleNamespace(
                        type="response.output_text.delta",
                        delta="xin",
                    )
                    yield {
                        "type": "response.output_text.delta",
                        "delta": " chào",
                    }
                    yield SimpleNamespace(type="response.completed")

                return stream()

        class FakeOpenAI:
            def __init__(self):
                self.responses = FakeResponses()
                self.chat = SimpleNamespace(completions=object())

        async def collect_response():
            client = FakeOpenAI()
            service = ChatService(
                codex_agent=None,
                openai_client=client,
                chat_model="gpt-5.4-nano",
            )

            chunks = [
                chunk
                async for chunk in service.stream_response(
                    character_slug="chi_pheo",
                    character_name="Chí Phèo",
                    user_message="bát cháo hành là gì?",
                    retrieval={
                        "context": "CONTEXT",
                        "sources": [],
                        "retrieval_mode": "test",
                    },
                )
            ]
            return client, chunks

        client, chunks = __import__("asyncio").run(collect_response())
        kwargs = client.responses.kwargs

        self.assertEqual(chunks, ["xin", " chào"])
        self.assertEqual(kwargs["model"], "gpt-5.4-nano")
        self.assertEqual(kwargs["input"], "bát cháo hành là gì?")
        self.assertTrue(kwargs["stream"])
        self.assertEqual(kwargs["reasoning"], {"effort": "none"})
        self.assertEqual(kwargs["text"], {"verbosity": "low"})
        self.assertIn("CONTEXT", kwargs["instructions"])
        self.assertNotIn("max_output_tokens", kwargs)
        self.assertNotIn("max_completion_tokens", kwargs)
        self.assertNotIn("max_tokens", kwargs)

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

    def test_format_chat_history_keeps_full_five_turn_context_by_default(self):
        history = []
        for turn in range(1, 6):
            history.append({"role": "user", "content": f"user turn {turn}"})
            history.append(
                {"role": "assistant", "content": f"character turn {turn}"}
            )

        formatted = ChatService._format_chat_history(history)

        self.assertIn("Student: user turn 1", formatted)
        self.assertIn("Character: character turn 1", formatted)
        self.assertIn("Student: user turn 5", formatted)
        self.assertIn("Character: character turn 5", formatted)
        self.assertEqual(formatted.count("Student:"), 5)
        self.assertEqual(formatted.count("Character:"), 5)

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
