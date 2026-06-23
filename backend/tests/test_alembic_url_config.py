import unittest
from configparser import ConfigParser


class AlembicUrlConfigTests(unittest.TestCase):
    def test_database_url_percent_chars_are_safe_for_configparser(self):
        from migrations.url_config import escape_configparser_value

        url = "postgresql+asyncpg://user:p%40ss%25word@db.example.com:5432/app"
        parser = ConfigParser()
        parser.add_section("alembic")

        parser.set("alembic", "sqlalchemy.url", escape_configparser_value(url))

        self.assertEqual(parser.get("alembic", "sqlalchemy.url"), url)


if __name__ == "__main__":
    unittest.main()
