import unittest
import json
from base64 import b64encode
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import itsdangerous
from fastapi.testclient import TestClient


def _join_paths(prefix, path):
    if not prefix:
        return path
    return f"{prefix.rstrip('/')}/{path.lstrip('/')}"


def _route_paths(routes, prefix=""):
    paths = set()
    for route in routes:
        path = getattr(route, "path", None)
        if path:
            paths.add(_join_paths(prefix, path))

        include_context = getattr(route, "include_context", None)
        nested_router = getattr(route, "original_router", None)
        nested_prefix = _join_paths(prefix, getattr(include_context, "prefix", ""))
        paths.update(_route_paths(getattr(nested_router, "routes", []), nested_prefix))
    return paths


class UserProgressModelTests(unittest.TestCase):
    def test_progress_is_unique_per_user(self):
        from models.db_models import UserProgress

        primary_keys = {column.name for column in UserProgress.__table__.primary_key}

        self.assertEqual(primary_keys, {"user_id"})


class UserProgressSchemaTests(unittest.TestCase):
    def test_payload_defaults_to_empty_progress(self):
        from models.schemas import UserProgressPayload

        payload = UserProgressPayload()

        self.assertEqual(payload.completed, {})
        self.assertEqual(payload.level_results, {})
        self.assertEqual(payload.skipped, [])


class UserProgressScoreTests(unittest.TestCase):
    def test_does_not_trust_client_awarded_progress_points(self):
        from services.db_postgres import calculate_progress_points

        level_results = {
            "xuan-toc-do": {
                "1": {"awarded": 9999999, "passed": True},
                "2": {"awarded": 50, "passed": True},
            },
            "chi-pheo": {
                "1": {"awarded": 50, "passed": True},
            },
        }

        self.assertEqual(calculate_progress_points(level_results), 0)

    def test_ignores_malformed_progress_points(self):
        from services.db_postgres import calculate_progress_points

        level_results = {
            "xuan-toc-do": {
                "1": {"awarded": "30"},
                "2": {"awarded": True},
                "3": {"awarded": 50},
            },
            "broken": None,
        }

        self.assertEqual(calculate_progress_points(level_results), 0)


class UserProgressRouteTests(unittest.TestCase):
    def setUp(self):
        from main import app

        self.app = app

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def _session_cookie(self, user_id):
        from api.session import SESSION_USER_ID_KEY
        from core.config import settings

        secret = settings.SESSION_SECRET_KEY or "vanver-dev-session-secret-change-me"
        signer = itsdangerous.TimestampSigner(secret)
        payload = b64encode(
            json.dumps({SESSION_USER_ID_KEY: str(user_id)}).encode("utf-8")
        )
        return signer.sign(payload).decode("utf-8")

    def _authenticated_client(self, user_id):
        from core.config import settings

        client = TestClient(self.app)
        self.addCleanup(client.close)
        client.cookies.set(
            settings.SESSION_COOKIE_NAME,
            self._session_cookie(user_id),
        )
        return client

    def test_progress_routes_are_registered(self):
        paths = _route_paths(self.app.routes)

        self.assertIn("/api/v1/users/{user_id}/progress", paths)

    def test_get_progress_returns_empty_state_when_missing(self):
        from api.deps import get_db
        from api.routes import users

        user_id = uuid4()
        user = SimpleNamespace(id=user_id)

        async def fake_get_db():
            yield object()

        self.app.dependency_overrides[get_db] = fake_get_db

        with (
            patch.object(users.db, "get_user", new=AsyncMock(return_value=user)),
            patch.object(
                users.db,
                "get_user_progress",
                new=AsyncMock(return_value=None),
            ),
        ):
            client = TestClient(self.app)
            self.addCleanup(client.close)
            response = client.get(f"/api/v1/users/{user_id}/progress")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "user_id": str(user_id),
                "completed": {},
                "level_results": {},
                "skipped": [],
                "updated_at": None,
            },
        )

    def test_put_progress_upserts_state(self):
        from api.deps import get_db
        from api.routes import users

        user_id = uuid4()
        updated_at = datetime.now(timezone.utc)
        user = SimpleNamespace(id=user_id)
        progress = SimpleNamespace(
            user_id=user_id,
            completed={"chi_pheo": {"passed": True}},
            level_results={"chi_pheo": {"1": {"passed": True}}},
            skipped=["mi"],
            updated_at=updated_at,
        )
        body_level_results = {"chi_pheo": {"1": {"passed": True, "awarded": 9999999}}}
        fake_session = object()

        async def fake_get_db():
            yield fake_session

        self.app.dependency_overrides[get_db] = fake_get_db

        with (
            patch.object(users.db, "get_user", new=AsyncMock(return_value=user)),
            patch.object(
                users.db,
                "upsert_user_progress",
                new=AsyncMock(return_value=progress),
            ) as upsert_progress,
        ):
            client = self._authenticated_client(user_id)
            response = client.put(
                f"/api/v1/users/{user_id}/progress",
                json={
                    "completed": progress.completed,
                    "level_results": body_level_results,
                    "skipped": progress.skipped,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["completed"], progress.completed)
        self.assertEqual(response.json()["level_results"], progress.level_results)
        self.assertEqual(response.json()["skipped"], progress.skipped)
        upsert_progress.assert_awaited_once_with(
            fake_session,
            user_id,
            completed=progress.completed,
            level_results=progress.level_results,
            skipped=progress.skipped,
        )

    def test_put_progress_requires_authenticated_session(self):
        from api.deps import get_db
        from api.routes import users

        user_id = uuid4()
        user = SimpleNamespace(id=user_id)
        progress = SimpleNamespace(
            user_id=user_id,
            completed={},
            level_results={},
            skipped=[],
            updated_at=None,
        )

        async def fake_get_db():
            yield object()

        self.app.dependency_overrides[get_db] = fake_get_db

        with (
            patch.object(users.db, "get_user", new=AsyncMock(return_value=user)),
            patch.object(
                users.db,
                "upsert_user_progress",
                new=AsyncMock(return_value=progress),
            ) as upsert_progress,
        ):
            client = TestClient(self.app)
            self.addCleanup(client.close)
            response = client.put(
                f"/api/v1/users/{user_id}/progress",
                json={"completed": {}, "level_results": {}, "skipped": []},
            )

        self.assertEqual(response.status_code, 401)
        upsert_progress.assert_not_awaited()

    def test_put_progress_requires_session_owner(self):
        from api.deps import get_db
        from api.routes import users

        user_id = uuid4()
        other_user_id = uuid4()
        user = SimpleNamespace(id=user_id)
        progress = SimpleNamespace(
            user_id=user_id,
            completed={},
            level_results={},
            skipped=[],
            updated_at=None,
        )

        async def fake_get_db():
            yield object()

        self.app.dependency_overrides[get_db] = fake_get_db

        with (
            patch.object(users.db, "get_user", new=AsyncMock(return_value=user)),
            patch.object(
                users.db,
                "upsert_user_progress",
                new=AsyncMock(return_value=progress),
            ) as upsert_progress,
        ):
            client = self._authenticated_client(other_user_id)
            response = client.put(
                f"/api/v1/users/{user_id}/progress",
                json={"completed": {}, "level_results": {}, "skipped": []},
            )

        self.assertEqual(response.status_code, 403)
        upsert_progress.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
