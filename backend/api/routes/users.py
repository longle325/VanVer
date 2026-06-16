"""
User registration / profile endpoints.

POST /api/v1/users          – disabled; users must sign in with OAuth
GET  /api/v1/users/{user_id} – get user profile
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from models.db_models import MatchStatus
from models.schemas import (
    MatchedCharacter,
    MatchedCharactersResponse,
    UserCreate,
    UserResponse,
)
from services import db_postgres as db

router = APIRouter(prefix="/users", tags=["users"])


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
    return user


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
