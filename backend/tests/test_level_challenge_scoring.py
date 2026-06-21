"""Tests for server-authoritative level-challenge scoring (issue #43).

Covers the trusted ledger helpers, retake idempotency, and the grade endpoint
(grading -> points, auth gating, validation).
"""

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


def _grade(score):
    return {
        "score": score,
        "passed": score == 1,
        "feedback": "ok",
        "matched_criteria": [],
        "missing_criteria": [],
        "confidence": 1.0,
        "retrieval_mode": "none",
        "sources": [],
    }


# ── Pure ledger helpers ─────────────────────────────────────────────────────


class CalculateProgressPointsTests(unittest.TestCase):
    def setUp(self):
        from services.db_postgres import calculate_progress_points

        self.calc = calculate_progress_points

    def test_none_and_empty(self):
        self.assertEqual(self.calc(None), 0)
        self.assertEqual(self.calc({}), 0)
        self.assertEqual(self.calc("nonsense"), 0)

    def test_sums_only_server_points(self):
        results = {
            "chi-pheo": {"1": {"server_points": 50}, "2": {"server_points": 30}},
            "mi": {"1": {"server_points": 20}},
        }
        self.assertEqual(self.calc(results), 100)

    def test_ignores_client_awarded_field(self):
        # A client cannot inflate score via the legacy `awarded` field.
        results = {"chi-pheo": {"1": {"awarded": 99999, "passed": True}}}
        self.assertEqual(self.calc(results), 0)

    def test_ignores_bool_and_malformed_slots(self):
        results = {
            "chi-pheo": {"1": {"server_points": True}},  # bool, not a score
            "mi": {"1": "garbage"},
            "bad": "garbage",
        }
        self.assertEqual(self.calc(results), 0)


class MergeServerOwnedTests(unittest.TestCase):
    def setUp(self):
        from services.db_postgres import _merge_server_owned_level_fields

        self.merge = _merge_server_owned_level_fields

    def test_preserves_server_points_against_client_save(self):
        # A stale client save can't revert server-graded progression, but its
        # non-server display fields survive.
        incoming = {
            "chi-pheo": {"1": {"passed": False, "score": 0, "openGrades": {"q": 1}}}
        }
        existing = {
            "chi-pheo": {
                "1": {"server_points": 50, "score": 5, "total": 5, "passed": True}
            }
        }
        merged = self.merge(incoming, existing)
        slot = merged["chi-pheo"]["1"]
        self.assertEqual(slot["server_points"], 50)
        self.assertEqual(slot["score"], 5)  # server value, not the client's 0
        self.assertEqual(slot["passed"], True)  # client can't revert to False
        self.assertEqual(slot["openGrades"], {"q": 1})  # display field kept

    def test_strips_client_supplied_server_fields(self):
        # Client tries to forge server-owned fields; none stored -> dropped.
        incoming = {"chi-pheo": {"1": {"server_points": 99999, "passed": True, "score": 5}}}
        existing = {}
        merged = self.merge(incoming, existing)
        self.assertNotIn("server_points", merged["chi-pheo"]["1"])
        self.assertNotIn("passed", merged["chi-pheo"]["1"])
        self.assertNotIn("score", merged["chi-pheo"]["1"])

    def test_client_forge_is_overwritten_by_stored_value(self):
        incoming = {"chi-pheo": {"1": {"server_points": 99999}}}
        existing = {"chi-pheo": {"1": {"server_points": 30}}}
        merged = self.merge(incoming, existing)
        self.assertEqual(merged["chi-pheo"]["1"]["server_points"], 30)

    def test_keeps_slots_client_omits(self):
        # A partial client sync must not drop a previously-earned score.
        incoming = {}
        existing = {"chi-pheo": {"1": {"server_points": 50, "passed": True}}}
        merged = self.merge(incoming, existing)
        self.assertEqual(merged["chi-pheo"]["1"]["server_points"], 50)


# ── Retake idempotency (record_level_award) ─────────────────────────────────


class RecordLevelAwardTests(unittest.IsolatedAsyncioTestCase):
    async def test_overwrites_prior_award_on_retake(self):
        from services import db_postgres

        progress = SimpleNamespace(
            level_results={"chi-pheo": {"1": {"server_points": 50, "passed": True}}},
            updated_at=None,
        )
        session = SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock(), add=lambda obj: None)

        with patch.object(
            db_postgres, "get_user_progress", new=AsyncMock(return_value=progress)
        ):
            # Retake the same level, now failing -> award drops to 30, not 50+30.
            await db_postgres.record_level_award(
                session, uuid4(), "chi-pheo", 1, 30, score=0, total=5, passed=False
            )

        self.assertEqual(progress.level_results["chi-pheo"]["1"]["server_points"], 30)
        # Server-graded progression is persisted in the same write.
        self.assertEqual(progress.level_results["chi-pheo"]["1"]["passed"], False)
        # And calculate sees the single, overwritten value.
        self.assertEqual(
            db_postgres.calculate_progress_points(progress.level_results), 30
        )

    async def test_adds_new_level_without_touching_others(self):
        from services import db_postgres

        progress = SimpleNamespace(
            level_results={"chi-pheo": {"1": {"server_points": 50}}},
            updated_at=None,
        )
        session = SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock(), add=lambda obj: None)

        with patch.object(
            db_postgres, "get_user_progress", new=AsyncMock(return_value=progress)
        ):
            await db_postgres.record_level_award(
                session, uuid4(), "chi-pheo", 2, 30, score=4, total=5, passed=True
            )

        self.assertEqual(
            db_postgres.calculate_progress_points(progress.level_results), 80
        )


# ── Grade endpoint ──────────────────────────────────────────────────────────


class LevelSubmitEndpointTests(unittest.TestCase):
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

    def _install_overrides(self, *, character, open_score):
        from api.deps import get_db, get_open_ended_grader

        async def fake_get_db():
            yield SimpleNamespace(commit=AsyncMock())

        self.app.dependency_overrides[get_db] = fake_get_db
        grader = SimpleNamespace(grade=AsyncMock(return_value=_grade(open_score)))
        self.app.dependency_overrides[get_open_ended_grader] = lambda: grader
        return grader

    def _post(self, client, user_id, character_id, level, answers):
        return client.post(
            "/api/v1/challenges/level/submit",
            json={
                "user_id": str(user_id),
                "character_id": str(character_id),
                "level": level,
                "answers": answers,
            },
        )

    def test_all_correct_passing_open_awards_full_points(self):
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(
            slug="chi-pheo", name="Chí Phèo", work_title="Chí Phèo"
        )
        self._install_overrides(character=character, open_score=1)

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), character, object())),
            ),
            patch.object(
                challenges.db, "record_level_award", new=AsyncMock()
            ) as record,
            patch.object(
                challenges.db,
                "get_effective_total_score",
                new=AsyncMock(return_value=50),
            ),
        ):
            # chi-pheo L1 keys are [1, 2, 0, 1]; essay graded 1 -> 5/5.
            resp = self._post(
                self._client(user_id),
                user_id,
                character_id,
                1,
                [1, 2, 0, 1, "luận điểm"],
            )

        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()
        self.assertEqual(body["score"], 5)
        self.assertEqual(body["total"], 5)
        self.assertTrue(body["passed"])
        self.assertEqual(body["points_earned"], 50)  # 30 + 20 pass bonus
        self.assertEqual(body["correct_answers"], [1, 2, 0, 1, -1])
        self.assertEqual(body["total_score"], 50)
        record.assert_awaited_once()
        # Awarded points come from the server, not the request.
        self.assertEqual(record.await_args.args[3], 1)  # level
        self.assertEqual(record.await_args.args[4], 50)  # points

    def test_underscore_db_slug_resolves_to_definition(self):
        # The DB stores slugs with underscores; grading must still find the
        # hyphen-keyed definition instead of 404-ing.
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(
            slug="chi_pheo", name="Chí Phèo", work_title="Chí Phèo"
        )
        self._install_overrides(character=character, open_score=1)

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), character, object())),
            ),
            patch.object(
                challenges.db, "record_level_award", new=AsyncMock()
            ) as record,
            patch.object(
                challenges.db,
                "get_effective_total_score",
                new=AsyncMock(return_value=50),
            ),
        ):
            resp = self._post(
                self._client(user_id),
                user_id,
                character_id,
                1,
                [1, 2, 0, 1, "luận điểm"],
            )

        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()["points_earned"], 50)
        # The award is recorded under the normalized hyphen slug so it lands on
        # the same level_results slot the client syncs.
        self.assertEqual(record.await_args.args[2], "chi-pheo")

    def test_all_wrong_failing_open_awards_completion_only(self):
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(
            slug="chi-pheo", name="Chí Phèo", work_title="Chí Phèo"
        )
        self._install_overrides(character=character, open_score=0)

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), character, object())),
            ),
            patch.object(challenges.db, "record_level_award", new=AsyncMock()),
            patch.object(
                challenges.db,
                "get_effective_total_score",
                new=AsyncMock(return_value=30),
            ),
        ):
            resp = self._post(
                self._client(user_id),
                user_id,
                character_id,
                1,
                [3, 3, 3, 3, "sai"],
            )

        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()
        self.assertEqual(body["score"], 0)
        self.assertFalse(body["passed"])
        self.assertEqual(body["points_earned"], 30)  # completion only

    def test_answer_count_mismatch_is_422(self):
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(
            slug="chi-pheo", name="Chí Phèo", work_title="Chí Phèo"
        )
        self._install_overrides(character=character, open_score=1)

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), character, object())),
            ),
            patch.object(
                challenges.db, "record_level_award", new=AsyncMock()
            ) as record,
        ):
            resp = self._post(
                self._client(user_id), user_id, character_id, 1, [1, 2, 0]
            )

        self.assertEqual(resp.status_code, 422)
        record.assert_not_awaited()

    def test_unknown_level_is_404(self):
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(slug="not-a-character", name="X", work_title="Y")
        self._install_overrides(character=character, open_score=1)

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), character, object())),
            ),
            patch.object(
                challenges.db, "record_level_award", new=AsyncMock()
            ) as record,
        ):
            resp = self._post(
                self._client(user_id), user_id, character_id, 1, [0, 0, 0, 0, "x"]
            )

        self.assertEqual(resp.status_code, 404)
        record.assert_not_awaited()

    def test_requires_authenticated_session(self):
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(
            slug="chi-pheo", name="Chí Phèo", work_title="Chí Phèo"
        )
        self._install_overrides(character=character, open_score=1)

        with patch.object(
            challenges.db, "record_level_award", new=AsyncMock()
        ) as record:
            resp = self._post(
                self._client(), user_id, character_id, 1, [1, 2, 0, 1, "x"]
            )

        self.assertEqual(resp.status_code, 401)
        record.assert_not_awaited()

    def test_legacy_submit_rejected_for_level_character(self):
        # The flat /challenges/submit must not award a character that has
        # phase-level challenges, or both ledgers could inflate the score.
        from api.deps import get_db
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(
            slug="chi_pheo", name="Chí Phèo", work_title="Chí Phèo"
        )

        async def fake_get_db():
            yield SimpleNamespace(commit=AsyncMock())

        self.app.dependency_overrides[get_db] = fake_get_db

        with (
            patch.object(
                challenges,
                "_validate_challenge_access",
                new=AsyncMock(return_value=(object(), character, object())),
            ),
            patch.object(challenges.db, "add_points", new=AsyncMock()) as add_points,
        ):
            resp = self._client(user_id).post(
                "/api/v1/challenges/submit",
                json={
                    "user_id": str(user_id),
                    "character_id": str(character_id),
                    "answers": [0, 1, 2, 3, 0],
                },
            )

        self.assertEqual(resp.status_code, 409)
        add_points.assert_not_awaited()

    def test_requires_session_owner(self):
        from api.routes import challenges

        user_id, character_id = uuid4(), uuid4()
        character = SimpleNamespace(
            slug="chi-pheo", name="Chí Phèo", work_title="Chí Phèo"
        )
        self._install_overrides(character=character, open_score=1)

        with patch.object(
            challenges.db, "record_level_award", new=AsyncMock()
        ) as record:
            resp = self._post(
                self._client(uuid4()), user_id, character_id, 1, [1, 2, 0, 1, "x"]
            )

        self.assertEqual(resp.status_code, 403)
        record.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
