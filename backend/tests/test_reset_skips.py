import json
import unittest
from base64 import b64encode
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import itsdangerous
from fastapi.testclient import TestClient


class ResetSkipsRouteTests(unittest.TestCase):
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

    def test_reset_skips_route_is_registered(self):
        paths = {getattr(r, "path", None) for r in self.app.routes}
        # nested routers expose their own paths; check the mounted prefix form
        self.assertTrue(
            any(
                "interactions/reset-skips" in (p or "")
                for p in self._all_paths()
            )
        )

    def _all_paths(self):
        paths = set()

        def walk(routes, prefix=""):
            for route in routes:
                path = getattr(route, "path", None)
                if path:
                    paths.add(prefix + path)
                include_context = getattr(route, "include_context", None)
                nested = getattr(route, "original_router", None)
                nested_prefix = prefix + getattr(include_context, "prefix", "")
                walk(getattr(nested, "routes", []), nested_prefix)

        walk(self.app.routes)
        return paths

    def test_reset_skips_clears_left_swipes_for_owner(self):
        from api.deps import get_db
        from api.routes import interactions

        user_id = uuid4()
        user = SimpleNamespace(id=user_id)

        async def fake_get_db():
            yield object()

        self.app.dependency_overrides[get_db] = fake_get_db

        with (
            patch.object(
                interactions.db, "get_user", new=AsyncMock(return_value=user)
            ),
            patch.object(
                interactions.db,
                "delete_left_swipes",
                new=AsyncMock(return_value=3),
            ) as delete_left,
        ):
            client = self._authenticated_client(user_id)
            response = client.post(
                "/api/v1/interactions/reset-skips",
                json={"user_id": str(user_id)},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cleared": 3})
        delete_left.assert_awaited_once()

    def test_reset_skips_requires_authenticated_session(self):
        from api.deps import get_db
        from api.routes import interactions

        user_id = uuid4()

        async def fake_get_db():
            yield object()

        self.app.dependency_overrides[get_db] = fake_get_db

        with patch.object(
            interactions.db,
            "delete_left_swipes",
            new=AsyncMock(return_value=0),
        ) as delete_left:
            client = TestClient(self.app)
            self.addCleanup(client.close)
            response = client.post(
                "/api/v1/interactions/reset-skips",
                json={"user_id": str(user_id)},
            )

        self.assertEqual(response.status_code, 401)
        delete_left.assert_not_awaited()

    def test_reset_skips_requires_session_owner(self):
        from api.deps import get_db
        from api.routes import interactions

        user_id = uuid4()
        other_user_id = uuid4()

        async def fake_get_db():
            yield object()

        self.app.dependency_overrides[get_db] = fake_get_db

        with patch.object(
            interactions.db,
            "delete_left_swipes",
            new=AsyncMock(return_value=0),
        ) as delete_left:
            client = self._authenticated_client(other_user_id)
            response = client.post(
                "/api/v1/interactions/reset-skips",
                json={"user_id": str(user_id)},
            )

        self.assertEqual(response.status_code, 403)
        delete_left.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
