import unittest

from scripts.seed_database import (
    CHARACTER_EVENT_SEEDS,
    CHARACTER_RELATIONSHIP_SEEDS,
    CHARACTER_SEEDS,
    DEMO_USER_SEEDS,
    challenge_payload,
)


class SeedDatabaseTests(unittest.TestCase):
    def test_character_seeds_cover_the_seeded_characters(self):
        self.assertEqual(
            {character["slug"] for character in CHARACTER_SEEDS},
            {
                "chi_pheo",
                "mi",
                "xuan_toc_do",
                "luc_van_tien",
                "thuy_kieu",
                "lao_hac",
                "chi_dau",
                "ong_sau",
                "ong_hai",
                "vu_nuong",
            },
        )

    def test_each_character_has_five_well_formed_challenge_questions(self):
        for character in CHARACTER_SEEDS:
            with self.subTest(slug=character["slug"]):
                questions = challenge_payload(character)
                self.assertEqual(len(questions), 5)
                for index, question in enumerate(questions, start=1):
                    self.assertEqual(question["id"], index)
                    self.assertEqual(len(question["options"]), 4)
                    self.assertIn(question["correct_answer_index"], range(4))
                    self.assertTrue(question["question"])
                    self.assertTrue(question["explanation"])

    def test_demo_users_have_distinct_names_and_scores(self):
        usernames = [user["username"] for user in DEMO_USER_SEEDS]

        self.assertEqual(len(usernames), len(set(usernames)))
        self.assertTrue(all(user["total_score"] > 0 for user in DEMO_USER_SEEDS))
        self.assertTrue(
            all(user["unlocked_character_slugs"] for user in DEMO_USER_SEEDS)
        )

    def test_demo_user_unlocked_characters_exist(self):
        character_slugs = {character["slug"] for character in CHARACTER_SEEDS}
        demo_unlocked_slugs = {
            slug
            for user in DEMO_USER_SEEDS
            for slug in user["unlocked_character_slugs"]
        }

        self.assertTrue(demo_unlocked_slugs)
        self.assertTrue(demo_unlocked_slugs.issubset(character_slugs))

    def test_relationship_and_event_seeds_cover_each_character(self):
        character_slugs = {character["slug"] for character in CHARACTER_SEEDS}

        self.assertEqual(set(CHARACTER_RELATIONSHIP_SEEDS), character_slugs)
        self.assertEqual(set(CHARACTER_EVENT_SEEDS), character_slugs)
        self.assertTrue(
            all(CHARACTER_RELATIONSHIP_SEEDS[slug] for slug in character_slugs)
        )
        self.assertTrue(all(CHARACTER_EVENT_SEEDS[slug] for slug in character_slugs))


if __name__ == "__main__":
    unittest.main()
