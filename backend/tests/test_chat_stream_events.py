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


if __name__ == "__main__":
    unittest.main()
