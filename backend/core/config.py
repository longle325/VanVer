"""
Application settings loaded from environment variables.

Resolution order (pydantic-settings default behaviour):
  1. OS / container environment variables  (Cloud Run, Docker, shell export)
  2. .env file (local development convenience)

In production (Cloud Run / Docker) there is no .env file — settings come
entirely from env vars injected by the platform.  Locally, developers can
use either `backend/.env` or the repo-root `.env` (shared with Vite).
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


def _find_env_files() -> list[str]:
    """Return .env paths that actually exist, closest first."""
    candidates = [
        Path(__file__).resolve().parents[1] / ".env",  # backend/.env
        Path(__file__).resolve().parents[2] / ".env",  # repo-root .env
    ]
    return [str(p) for p in candidates if p.is_file()]


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vanver"

    # --- OpenAI ---
    OPENAI_API_KEY: str = ""
    CODEX_MODEL: str = "codex-mini"
    CHAT_MODEL: str = "gpt-5.4-nano"
    CHAT_REASONING_EFFORT: str = "none"
    CHAT_RESPONSE_VERBOSITY: str = "low"
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 3072

    # --- Codex Knowledge Base ---
    KNOWLEDGE_BASE_DIR: str = "./knowledge_base"
    RAG_TOP_K: int = 5
    RAG_MIN_SIMILARITY: float = 0.0

    # --- CORS ---
    # Vite may pick any free port (5173, 5169, etc.) so allow a range.
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5169",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5169",
        "http://localhost:3000",
        "capacitor://localhost",  # iOS Capacitor
        "https://localhost",  # Android Capacitor
    ]

    # --- Auth / OAuth ---
    SESSION_SECRET_KEY: str = ""
    SESSION_COOKIE_NAME: str = "vanver_session"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 14

    OAUTH_POST_LOGIN_REDIRECT: str = "http://localhost:5173"
    OAUTH_ALLOWED_REDIRECT_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "capacitor://localhost",
        "https://localhost",
    ]
    OAUTH_CALLBACK_BASE_URL: str = ""

    OAUTH_GOOGLE_CLIENT_ID: str = ""
    OAUTH_GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_GOOGLE_SERVER_METADATA_URL: str = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    OAUTH_GOOGLE_SCOPE: str = "openid email profile"

    # --- App ---
    APP_TITLE: str = "Vanver API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Points ---
    POINTS_MATCH: int = 10
    POINTS_CHALLENGE_COMPLETE: int = 50
    POINTS_CHALLENGE_PASS_BONUS: int = 40  # >= 4/5
    CHALLENGE_PASS_THRESHOLD: int = 4  # out of 5
    POINTS_LEVEL_COMPLETE: int = 30
    POINTS_LEVEL_PASS_BONUS: int = 20  # >= 4/5 in a phase level

    # --- Chat quota / prompt cost controls ---
    CHAT_MONTHLY_CHARACTER_LIMIT: int = 5
    CHAT_MONTHLY_MESSAGES_PER_CHARACTER_LIMIT: int = 5
    CHAT_PROMPT_HISTORY_MAX_MESSAGES: int = 3
    CHAT_PROMPT_HISTORY_MAX_CHARS_PER_MESSAGE: int = 400
    CHAT_PROMPT_HISTORY_MAX_TOTAL_CHARS: int = 1200

    model_config = {
        # Tuple of .env paths — pydantic reads the first one found.
        # Empty tuple is fine (no .env in production containers).
        "env_file": tuple(_find_env_files()) or (".env",),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
