import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from api.routes.chat import chat_event_generator


class ChatStreamEventTests(unittest.TestCase):
    def test_stream_yields_ready_before_retrieval_runs(self):
        class FakeChatService:
            def __init__(self):
                self.prepare_called = False

            async def prepare_retrieval(self, **kwargs):
                self.prepare_called = True
                return {
                    "context": "context",
                    "retrieval_mode": "test",
                    "sources": [],
                }

            async def stream_response(self, **kwargs):
                yield "xin chào"

        async def read_first_event():
            service = FakeChatService()
            generator = chat_event_generator(
                session=SimpleNamespace(),
                chat_service=service,
                user_id=uuid4(),
                character_id=uuid4(),
                character=SimpleNamespace(
                    slug="chi_pheo",
                    name="Chí Phèo",
                    voice_instructions=None,
                ),
                user_message="bát cháo hành là gì?",
                chat_history=[],
                create_chat_message=AsyncMock(),
            )

            first_event = await anext(generator)
            await generator.aclose()
            return service, first_event

        service, first_event = asyncio.run(read_first_event())

        self.assertEqual(first_event, {"event": "ready", "data": "{}"})
        self.assertFalse(service.prepare_called)

    def test_stream_short_circuits_guardrail_response_before_retrieval(self):
        class FakeChatService:
            def guardrail_response(self, **kwargs):
                return "Chuyện ấy không thuộc phần đời của Lão Hạc."

            async def prepare_retrieval(self, **kwargs):
                raise AssertionError("retrieval should not run for guardrail replies")

            async def stream_response(self, **kwargs):
                raise AssertionError("model stream should not run for guardrail replies")
                yield ""

        async def read_events():
            create_message = AsyncMock()
            generator = chat_event_generator(
                session=SimpleNamespace(),
                chat_service=FakeChatService(),
                user_id=uuid4(),
                character_id=uuid4(),
                character=SimpleNamespace(
                    slug="lao_hac",
                    name="Lão Hạc",
                    voice_instructions=None,
                ),
                user_message="1+1= mấy?",
                chat_history=[],
                create_chat_message=create_message,
            )

            events = []
            async for event in generator:
                events.append(event)
            return events, create_message

        events, create_message = asyncio.run(read_events())

        self.assertEqual(events[0], {"event": "ready", "data": "{}"})
        self.assertEqual(
            events[1],
            {"data": "Chuyện ấy không thuộc phần đời của Lão Hạc."},
        )
        self.assertEqual(create_message.await_count, 2)


if __name__ == "__main__":
    unittest.main()
