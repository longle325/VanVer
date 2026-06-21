import unittest
from pathlib import Path
from unittest.mock import patch


class EnvConfigTests(unittest.TestCase):
    def test_backend_reads_only_repo_root_env_file(self):
        from core import config as config_module

        repo_root = Path(config_module.__file__).resolve().parents[2]

        with patch.object(Path, "is_file", return_value=True):
            self.assertEqual(
                config_module._find_env_files(),
                [str(repo_root / ".env")],
            )

    def test_repo_uses_single_root_env_example(self):
        repo_root = Path(__file__).resolve().parents[2]

        self.assertTrue((repo_root / ".env.example").is_file())
        self.assertFalse((repo_root / "backend/.env.example").exists())
        self.assertFalse((repo_root / "frontend/.env.example").exists())


if __name__ == "__main__":
    unittest.main()
