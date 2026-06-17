import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient


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


class UserProgressRouteTests(unittest.TestCase):
    def setUp(self):
        from main import app

        self.app = app

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def test_progress_routes_are_registered(self):
        paths = {route.path for route in self.app.routes}

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
                json={
                    "completed": progress.completed,
                    "level_results": progress.level_results,
                    "skipped": progress.skipped,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["completed"], progress.completed)
        self.assertEqual(response.json()["level_results"], progress.level_results)
        self.assertEqual(response.json()["skipped"], progress.skipped)
        upsert_progress.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
