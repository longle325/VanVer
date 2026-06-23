import unittest
from types import SimpleNamespace
from uuid import uuid4


class LeaderboardDisplayNameTests(unittest.IsolatedAsyncioTestCase):
    async def test_leaderboard_prefers_display_name_over_username(self):
        from services.db_postgres import get_leaderboard

        user_id = uuid4()
        rows = [
            SimpleNamespace(
                user_id=user_id,
                username="student",
                display_name="Student One",
                total_score=90,
                level_results={},
                characters_unlocked=3,
            )
        ]

        class FakeResult:
            def all(self):
                return rows

        class FakeSession:
            async def execute(self, _stmt):
                return FakeResult()

        entries = await get_leaderboard(FakeSession())

        self.assertEqual(entries[0]["username"], "Student One")

    async def test_leaderboard_falls_back_to_username_without_display_name(self):
        from services.db_postgres import get_leaderboard

        rows = [
            SimpleNamespace(
                user_id=uuid4(),
                username="student",
                display_name=None,
                total_score=90,
                level_results={},
                characters_unlocked=3,
            )
        ]

        class FakeResult:
            def all(self):
                return rows

        class FakeSession:
            async def execute(self, _stmt):
                return FakeResult()

        entries = await get_leaderboard(FakeSession())

        self.assertEqual(entries[0]["username"], "student")


if __name__ == "__main__":
    unittest.main()
