"""
Vanver API  –  FastAPI application factory.

Start locally:
    uvicorn main:app --reload --port 8081
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.config import settings
from core.database import Base, engine, ensure_vector_extension

# Route modules
from api.routes import (
    admin,
    auth,
    challenges,
    characters,
    chat,
    deck,
    interactions,
    leaderboard,
    users,
)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup, dispose engine on shutdown."""
    logger.info("Starting Vanver API …")
    await ensure_vector_extension()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Shutting down …")
    await engine.dispose()


# ── App ───────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


def _expand_origins(origins: list[str]) -> list[str]:
    """Allow any localhost port in dev so Vite port changes don't break CORS."""
    expanded = list(origins)
    for origin in origins:
        if "://localhost:" in origin or "://127.0.0.1:" in origin:
            # Add a wildcard-port variant isn't supported by CORS spec,
            # so just add common Vite ports.
            host = origin.rsplit(":", 1)[0]  # e.g. "http://localhost"
            for port in (3000, 4173, 5169, 5173, 5174, 8080):
                candidate = f"{host}:{port}"
                if candidate not in expanded:
                    expanded.append(candidate)
    return expanded


app.add_middleware(
    CORSMiddleware,
    allow_origins=_expand_origins(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY or "vanver-dev-session-secret-change-me",
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE_SECONDS,
    same_site=settings.SESSION_COOKIE_SAMESITE,
    https_only=settings.SESSION_COOKIE_SECURE,
)

# ── Routes ────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(users.router, prefix=API_PREFIX)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(deck.router, prefix=API_PREFIX)
app.include_router(interactions.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)
app.include_router(challenges.router, prefix=API_PREFIX)
app.include_router(leaderboard.router, prefix=API_PREFIX)
app.include_router(characters.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}
