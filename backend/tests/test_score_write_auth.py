import json
import unittest
from base64 import b64encode
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import itsdangerous
from fastapi.testclient import TestClient


def _session_cookie(user_id):
    from api.session import SESSION_USER_ID_KEY
    from core.config import settings

    secret = settings.SESSION_SECRET_KEY or "vanver-dev-session-secret-change-me"
    signer = itsdangerous.TimestampSigner(secret)
    payload = b64encode(
        json.dumps({SESSION_USER_ID_KEY: str(user_id)}).encode("utf-8")
    )
    return signer.sign(payload).decode("utf-8")


class ScoreWriteAuthTests(unittest.TestCase):
    def setUp(self):
        from main import app

        self.app = app

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def _client(self, user_id=None):
        from core.config import settings

        client = TestClient(self.app)
        self.addCleanup(client.close)
        if user_id is not None:
            client.cookies.set(settings.SESSION_COOKIE_NAME, _session_cookie(user_id))
        return client

    def _install_fake_db(self):
        from api.deps import get_db

        async def fake_get_db():
            yield SimpleNamespace(commit=AsyncMock())

        self.app.dependency_overrides[get_db] = fake_get_db

    def test_swipe_requires_authenticated_session(self):
        from api.routes import interactions

        self._install_fake_db()
        user_id = uuid4()
        character_id = uuid4()

        with (
            patch.object(interactions.db, "get_user", new=AsyncMock(return_value=object())),
            patch.object(
                interactions.db,
                "get_character",
                new=AsyncMock(return_value=object()),
            ),
            patch.object(interactions.db, "get_match", new=AsyncMock(return_value=None)),
            patch.object(interactions.db, "create_match", new=AsyncMock()),
            patch.object(interactions.db, "add_points", new=AsyncMock()) as add_points,
        ):
            response = self._client().post(
                "/api/v1/interactions/swipe",
                json={
                    "user_id": str(user_id),
                    "character_id": str(character_id),
                    "direction": "right",
                },
            )

        self.assertEqual(response.status_code, 401)
        add_points.assert_not_awaited()

    def test_swipe_requires_session_owner(self):
        from api.routes import interactions

        self._install_fake_db()
        user_id = uuid4()
        character_id = uuid4()

        with (
            patch.object(interactions.db, "get_user", new=AsyncMock(return_value=object())),
            patch.object(
                interactions.db,
                "get_character",
                new=AsyncMock(return_value=object()),
            ),
            patch.object(interactions.db, "get_match", new=AsyncMock(return_value=None)),
            patch.object(interactions.db, "create_match", new=AsyncMock()),
            patch.object(interactions.db, "add_points", new=AsyncMock()) as add_points,
        ):
            response = self._client(uuid4()).post(
                "/api/v1/interactions/swipe",
                json={
                    "user_id": str(user_id),
                    "character_id": str(character_id),
                    "direction": "right",
                },
            )

        self.assertEqual(response.status_code, 403)
        add_points.assert_not_awaited()

    def test_submit_challenge_requires_authenticated_session(self):
        from api.routes import challenges

        self._install_fake_db()
        user_id = uuid4()
        character_id = uuid4()

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), object(), object())),
            ),
            patch.object(
                challenges.db,
                "get_challenge_for_character",
                new=AsyncMock(
                    return_value=SimpleNamespace(
                        questions=[
                            {
                                "correct_answer_index": 0,
                                "explanation": "ok",
                            }
                        ]
                    )
                ),
            ),
            patch.object(
                challenges.db,
                "get_challenge_attempt",
                new=AsyncMock(return_value=None),
            ),
            patch.object(challenges.db, "create_challenge_attempt", new=AsyncMock()),
            patch.object(challenges.db, "add_points", new=AsyncMock()) as add_points,
        ):
            response = self._client().post(
                "/api/v1/challenges/submit",
                json={
                    "user_id": str(user_id),
                    "character_id": str(character_id),
                    "answers": [0],
                },
            )

        self.assertEqual(response.status_code, 401)
        add_points.assert_not_awaited()

    def test_submit_challenge_requires_session_owner(self):
        from api.routes import challenges

        self._install_fake_db()
        user_id = uuid4()
        character_id = uuid4()

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), object(), object())),
            ),
            patch.object(
                challenges.db,
                "get_challenge_for_character",
                new=AsyncMock(
                    return_value=SimpleNamespace(
                        questions=[
                            {
                                "correct_answer_index": 0,
                                "explanation": "ok",
                            }
                        ]
                    )
                ),
            ),
            patch.object(
                challenges.db,
                "get_challenge_attempt",
                new=AsyncMock(return_value=None),
            ),
            patch.object(challenges.db, "create_challenge_attempt", new=AsyncMock()),
            patch.object(challenges.db, "add_points", new=AsyncMock()) as add_points,
        ):
            response = self._client(uuid4()).post(
                "/api/v1/challenges/submit",
                json={
                    "user_id": str(user_id),
                    "character_id": str(character_id),
                    "answers": [0],
                },
            )

        self.assertEqual(response.status_code, 403)
        add_points.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
