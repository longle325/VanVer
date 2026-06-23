import unittest


class AlembicBaselineTests(unittest.TestCase):
    def test_full_legacy_schema_without_version_table_should_be_stamped(self):
        from migrations.baseline import should_stamp_legacy_schema

        model_tables = {"users", "characters", "matches"}
        existing_tables = {"users", "characters", "matches", "extra_table"}

        self.assertTrue(should_stamp_legacy_schema(existing_tables, model_tables))

    def test_versioned_or_partial_schema_should_not_be_stamped(self):
        from migrations.baseline import should_stamp_legacy_schema

        model_tables = {"users", "characters", "matches"}

        self.assertFalse(
            should_stamp_legacy_schema(
                {"alembic_version", "users", "characters", "matches"},
                model_tables,
            )
        )
        self.assertFalse(should_stamp_legacy_schema({"users"}, model_tables))
        self.assertFalse(should_stamp_legacy_schema(set(), model_tables))


if __name__ == "__main__":
    unittest.main()
