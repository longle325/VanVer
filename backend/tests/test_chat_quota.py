import asyncio
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi import HTTPException

from api.routes.chat import _resolve_chat_user_id
from services.chat_quota import (
    ChatQuotaExceeded,
    enforce_monthly_chat_quota,
    month_start_utc,
)


class ChatQuotaTests(unittest.TestCase):
    def test_month_start_utc_uses_the_current_utc_month(self):
        now = datetime(2026, 6, 16, 8, 30, tzinfo=timezone.utc)

        self.assertEqual(
            month_start_utc(now),
            datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
        )

    def test_allows_the_fifth_monthly_message_for_an_existing_character(self):
        session = object()
        user_id = uuid4()
        character_id = uuid4()
        now = datetime(2026, 6, 16, 8, 30, tzinfo=timezone.utc)

        with patch(
            "services.chat_quota.db.get_monthly_chat_quota_usage",
            new=AsyncMock(
                return_value={
                    "used_characters": 5,
                    "messages_for_character": 4,
                }
            ),
        ) as get_usage:
            asyncio.run(
                enforce_monthly_chat_quota(
                    session,
                    user_id=user_id,
                    character_id=character_id,
                    now=now,
                    character_limit=5,
                    messages_per_character_limit=5,
                )
            )

        get_usage.assert_awaited_once_with(
            session,
            user_id=user_id,
            character_id=character_id,
            since=datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
        )

    def test_blocks_a_sixth_character_in_the_same_month(self):
        with patch(
            "services.chat_quota.db.get_monthly_chat_quota_usage",
            new=AsyncMock(
                return_value={
                    "used_characters": 5,
                    "messages_for_character": 0,
                }
            ),
        ):
            with self.assertRaises(ChatQuotaExceeded) as exc:
                asyncio.run(
                    enforce_monthly_chat_quota(
                        object(),
                        user_id=uuid4(),
                        character_id=uuid4(),
                        now=datetime(2026, 6, 16, tzinfo=timezone.utc),
                        character_limit=5,
                        messages_per_character_limit=5,
                    )
                )

        self.assertEqual(exc.exception.status_code, 402)
        self.assertEqual(exc.exception.detail["limit_type"], "monthly_character_limit")
        self.assertEqual(exc.exception.detail["limit"], 5)
        self.assertEqual(exc.exception.detail["reset_at"], "2026-07-01T00:00:00+00:00")

    def test_blocks_a_sixth_message_for_the_same_character_in_the_same_month(self):
        with patch(
            "services.chat_quota.db.get_monthly_chat_quota_usage",
            new=AsyncMock(
                return_value={
                    "used_characters": 3,
                    "messages_for_character": 5,
                }
            ),
        ):
            with self.assertRaises(ChatQuotaExceeded) as exc:
                asyncio.run(
                    enforce_monthly_chat_quota(
                        object(),
                        user_id=uuid4(),
                        character_id=uuid4(),
                        now=datetime(2026, 6, 16, tzinfo=timezone.utc),
                        character_limit=5,
                        messages_per_character_limit=5,
                    )
                )

        self.assertEqual(exc.exception.status_code, 402)
        self.assertEqual(
            exc.exception.detail["limit_type"],
            "monthly_messages_per_character_limit",
        )
        self.assertEqual(exc.exception.detail["limit"], 5)


class ChatSessionUserResolutionTests(unittest.TestCase):
    def test_authenticated_session_user_can_omit_body_user_id(self):
        user_id = uuid4()
        request = SimpleNamespace(session={"user_id": str(user_id)})

        self.assertEqual(_resolve_chat_user_id(request, None), user_id)

    def test_authenticated_session_user_must_match_body_user_id(self):
        request = SimpleNamespace(session={"user_id": str(uuid4())})

        with self.assertRaises(HTTPException) as exc:
            _resolve_chat_user_id(request, uuid4())

        self.assertEqual(exc.exception.status_code, 403)

    def test_legacy_body_user_id_is_allowed_when_session_is_absent(self):
        user_id = uuid4()
        request = SimpleNamespace(session={})

        self.assertEqual(_resolve_chat_user_id(request, user_id), user_id)

    def test_missing_session_and_body_user_id_is_unauthorized(self):
        request = SimpleNamespace(session={})

        with self.assertRaises(HTTPException) as exc:
            _resolve_chat_user_id(request, None)

        self.assertEqual(exc.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
