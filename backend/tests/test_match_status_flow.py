import unittest

from models.db_models import MatchStatus as DbMatchStatus
from models.schemas import MatchStatus as ApiMatchStatus
from services.db_postgres import UNLOCKED_MATCH_STATUSES


class MatchStatusFlowTests(unittest.TestCase):
    def test_match_status_includes_left_swipe_state(self):
        self.assertEqual(DbMatchStatus.SWIPED_LEFT.value, "SWIPED_LEFT")
        self.assertEqual(ApiMatchStatus.SWIPED_LEFT.value, "SWIPED_LEFT")

    def test_unlocked_statuses_exclude_left_swipes(self):
        unlocked_statuses = {
            DbMatchStatus.SWIPED_RIGHT,
            DbMatchStatus.CHAT_UNLOCKED,
            DbMatchStatus.CHALLENGE_PASSED,
        }

        self.assertNotIn(DbMatchStatus.SWIPED_LEFT, unlocked_statuses)

    def test_leaderboard_unlocked_statuses_match_status_flow(self):
        self.assertEqual(
            set(UNLOCKED_MATCH_STATUSES),
            {
                DbMatchStatus.SWIPED_RIGHT,
                DbMatchStatus.CHAT_UNLOCKED,
                DbMatchStatus.CHALLENGE_PASSED,
            },
        )
        self.assertNotIn(DbMatchStatus.SWIPED_LEFT, UNLOCKED_MATCH_STATUSES)


if __name__ == "__main__":
    unittest.main()
