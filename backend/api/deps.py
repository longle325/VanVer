"""
FastAPI dependency injection helpers.
"""

from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_factory
from services.chat_service import ChatService, get_chat_service
from services.codex_agent import CodexKnowledgeAgent, get_codex_agent
from services.knowledge_retriever import KnowledgeRetriever, get_knowledge_retriever
from services.open_ended_grading_service import (
    OpenEndedGradingService,
    get_open_ended_grading_service,
)


# ── Database session ──────────────────────────────────────────────────────


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield an async DB session, then close it."""
    async with async_session_factory() as session:
        yield session


# ── Codex agent ───────────────────────────────────────────────────────────


def get_codex() -> CodexKnowledgeAgent:
    return get_codex_agent()


# ── Chat service ──────────────────────────────────────────────────────────


def get_chat() -> ChatService:
    return get_chat_service(
        codex_agent=get_codex(),
        knowledge_retriever=get_retriever(),
    )


# ── Knowledge retriever ────────────────────────────────────────────────────


def get_retriever() -> KnowledgeRetriever:
    return get_knowledge_retriever()


# ── Open-ended challenge grading ──────────────────────────────────────────


def get_open_ended_grader() -> OpenEndedGradingService:
    return get_open_ended_grading_service(knowledge_retriever=get_retriever())
