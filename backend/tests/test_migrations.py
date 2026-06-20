import importlib
import unittest


class InitialMigrationTests(unittest.TestCase):
    def test_named_enums_are_created_explicitly_only_once(self):
        migration = importlib.import_module("migrations.versions.0001_initial_schema")

        self.assertFalse(migration.match_status.create_type)
        self.assertFalse(migration.chat_role.create_type)


if __name__ == "__main__":
    unittest.main()
