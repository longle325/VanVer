import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient


class OAuthServiceTests(unittest.TestCase):
    def test_normalizes_oidc_userinfo_into_profile(self):
        from services.oauth_service import normalize_oidc_userinfo

        profile = normalize_oidc_userinfo(
            "google",
            {
                "sub": "google-user-123",
                "email": "Student@Example.COM",
                "email_verified": True,
                "name": "Student One",
            },
        )

        self.assertEqual(profile.provider, "google")
        self.assertEqual(profile.subject, "google-user-123")
        self.assertEqual(profile.email, "student@example.com")
        self.assertEqual(profile.display_name, "Student One")
        self.assertEqual(profile.username_seed, "student")

    def test_rejects_oidc_userinfo_without_subject(self):
        from services.oauth_service import normalize_oidc_userinfo

        with self.assertRaises(ValueError):
            normalize_oidc_userinfo("google", {"email": "student@example.com"})

    def test_safe_redirect_target_rejects_open_redirects(self):
        from services.oauth_service import safe_post_login_redirect

        default = "http://localhost:5173"
        allowed = ["http://localhost:5173", "capacitor://localhost"]

        self.assertEqual(
            safe_post_login_redirect("/profile", default, allowed),
            "http://localhost:5173/profile",
        )
        self.assertEqual(
            safe_post_login_redirect("http://localhost:5173/chat", default, allowed),
            "http://localhost:5173/chat",
        )
        self.assertEqual(
            safe_post_login_redirect("https://evil.example/phish", default, allowed),
            default,
        )
        self.assertEqual(
            safe_post_login_redirect("//evil.example/phish", default, allowed),
            default,
        )


class OAuthModelTests(unittest.TestCase):
    def test_user_model_has_oauth_identity_columns(self):
        from models.db_models import User

        columns = set(User.__table__.columns.keys())

        self.assertIn("email", columns)
        self.assertIn("display_name", columns)
        self.assertIn("auth_provider", columns)
        self.assertIn("auth_subject", columns)
        self.assertIn("last_login_at", columns)

    def test_oauth_identity_is_unique_per_provider_subject(self):
        from models.db_models import User

        constraint_names = {
            constraint.name for constraint in User.__table__.constraints
        }

        self.assertIn("uq_users_auth_provider_subject", constraint_names)


class OAuthRouteTests(unittest.TestCase):
    def setUp(self):
        from main import app

        self.app = app

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def test_auth_routes_are_registered(self):
        paths = {route.path for route in self.app.routes}

        self.assertIn("/api/v1/auth/login/{provider}", paths)
        self.assertIn("/api/v1/auth/callback/{provider}", paths)
        self.assertIn("/api/v1/auth/me", paths)
        self.assertIn("/api/v1/auth/logout", paths)

    def test_me_requires_an_authenticated_session(self):
        client = TestClient(self.app)
        self.addCleanup(client.close)

        response = client.get("/api/v1/auth/me")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated.")

    def test_callback_upserts_user_and_sets_session(self):
        from api.deps import get_db
        from api.routes import auth

        user_id = uuid4()
        user = SimpleNamespace(
            id=user_id,
            username="student",
            grade_level=10,
            total_score=0,
            email="student@example.com",
            display_name="Student One",
            created_at=datetime.now(timezone.utc),
        )

        class FakeOAuthClient:
            async def authorize_access_token(self, request):
                return {
                    "id_token": "id-token-value",
                    "userinfo": {
                        "sub": "google-user-123",
                        "email": "student@example.com",
                        "name": "Student One",
                    },
                }

        async def fake_get_db():
            yield object()

        self.app.dependency_overrides[get_db] = fake_get_db
        self.app.dependency_overrides[auth.get_oauth_client] = (
            lambda provider: FakeOAuthClient()
        )

        with (
            patch.object(
                auth.db,
                "upsert_oauth_user",
                new=AsyncMock(return_value=user),
            ) as upsert_user,
            patch.object(auth.db, "get_user", new=AsyncMock(return_value=user)),
        ):
            client = TestClient(self.app)
            self.addCleanup(client.close)
            response = client.get(
                "/api/v1/auth/callback/google?code=abc&state=xyz",
                follow_redirects=False,
            )

            self.assertEqual(response.status_code, 303)
            self.assertEqual(response.headers["location"], "http://localhost:5173")
            upsert_user.assert_awaited_once()

            me = client.get("/api/v1/auth/me")
            self.assertEqual(me.status_code, 200)
            self.assertEqual(me.json()["id"], str(user_id))
            self.assertEqual(me.json()["email"], "student@example.com")

    def test_logout_clears_session(self):
        client = TestClient(self.app)
        self.addCleanup(client.close)

        response = client.post("/api/v1/auth/logout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        self.assertIn("litmatch_session=", response.headers.get("set-cookie", ""))


if __name__ == "__main__":
    unittest.main()
