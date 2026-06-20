"""
User registration / profile endpoints.

POST /api/v1/users          – disabled; users must sign in with OAuth
GET  /api/v1/users/{user_id} – get user profile
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from api.routes.auth import SESSION_USER_ID_KEY
from models.db_models import MatchStatus
from models.schemas import (
    MatchedCharacter,
    MatchedCharactersResponse,
    UserCreate,
    UserProgressPayload,
    UserProgressResponse,
    UserResponse,
)
from services import db_postgres as db

router = APIRouter(prefix="/users", tags=["users"])


def _session_user_id(request: Request) -> UUID | None:
    value = request.session.get(SESSION_USER_ID_KEY)
    if not value:
        return None
    try:
        return UUID(str(value))
    except ValueError:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )


def _require_progress_owner(request: Request, user_id: UUID) -> None:
    session_user_id = _session_user_id(request)
    if session_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    if session_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated session does not match request user.",
        )


def _strip_client_awards(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_client_awards(item)
            for key, item in value.items()
            if key != "awarded"
        }
    if isinstance(value, list):
        return [_strip_client_awards(item) for item in value]
    return value


@router.post(
    "",
    status_code=status.HTTP_410_GONE,
)
async def create_user(
    _body: UserCreate,
):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Direct user creation is disabled. Use OAuth login.",
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    user = await db.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    total_score = await db.get_effective_total_score(session, user)
    return UserResponse.model_validate(user).model_copy(
        update={"total_score": total_score}
    )


@router.get("/{user_id}/matches", response_model=MatchedCharactersResponse)
async def get_user_matched_characters(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    user = await db.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    matches = await db.get_user_matches(
        session,
        user_id,
        statuses=[
            MatchStatus.SWIPED_RIGHT,
            MatchStatus.CHAT_UNLOCKED,
            MatchStatus.CHALLENGE_PASSED,
        ],
    )
    characters = [
        MatchedCharacter(
            **match.character.__dict__,
            match_status=match.status,
            matched_at=match.created_at,
        )
        for match in matches
    ]
    return MatchedCharactersResponse(characters=characters)


@router.get("/{user_id}/progress", response_model=UserProgressResponse)
async def get_user_progress(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    user = await db.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    progress = await db.get_user_progress(session, user_id)
    if progress is None:
        return UserProgressResponse(
            user_id=user_id,
            completed={},
            level_results={},
            skipped=[],
            updated_at=None,
        )

    return UserProgressResponse(
        user_id=progress.user_id,
        completed=progress.completed,
        level_results=progress.level_results,
        skipped=progress.skipped,
        updated_at=progress.updated_at,
    )


@router.put("/{user_id}/progress", response_model=UserProgressResponse)
async def save_user_progress(
    request: Request,
    user_id: UUID,
    body: UserProgressPayload,
    session: AsyncSession = Depends(get_db),
):
    _require_progress_owner(request, user_id)

    user = await db.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    progress = await db.upsert_user_progress(
        session,
        user_id,
        completed=body.completed,
        level_results=_strip_client_awards(body.level_results),
        skipped=body.skipped,
    )
    return UserProgressResponse(
        user_id=progress.user_id,
        completed=progress.completed,
        level_results=progress.level_results,
        skipped=progress.skipped,
        updated_at=progress.updated_at,
    )
