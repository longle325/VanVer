"""
Swipe interaction endpoint.

POST /api/v1/interactions/swipe
  Records a left/right swipe.  If right, creates a match and awards points.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from api.session import require_session_owner
from core.config import settings
from models.db_models import MatchStatus as DbMatchStatus
from models.schemas import MatchStatus, SwipeDirection, SwipeRequest, SwipeResponse
from services import db_postgres as db

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/swipe", response_model=SwipeResponse)
async def swipe(
    request: Request,
    body: SwipeRequest,
    session: AsyncSession = Depends(get_db),
):
    require_session_owner(request, body.user_id)

    # Validate user and character exist
    user = await db.get_user(session, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    character = await db.get_character(session, body.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found.")

    existing = await db.get_match(session, body.user_id, body.character_id)

    # Left swipe → save skip state so the deck does not show this card again.
    if body.direction == SwipeDirection.LEFT:
        if existing is None:
            await db.create_match(
                session,
                body.user_id,
                body.character_id,
                status=DbMatchStatus.SWIPED_LEFT,
            )
        return SwipeResponse(
            matched=False,
            points_earned=0,
            match_status=MatchStatus.SWIPED_LEFT,
        )

    # Right swipe → create match + award points
    if existing and existing.status != DbMatchStatus.SWIPED_LEFT:
        raise HTTPException(
            status_code=409,
            detail="Already matched with this character.",
        )

    if existing and existing.status == DbMatchStatus.SWIPED_LEFT:
        await db.update_match_status(
            session,
            body.user_id,
            body.character_id,
            DbMatchStatus.SWIPED_RIGHT,
        )
    else:
        await db.create_match(session, body.user_id, body.character_id)
    await db.add_points(session, body.user_id, settings.POINTS_MATCH)

    return SwipeResponse(
        matched=True,
        points_earned=settings.POINTS_MATCH,
        match_status=MatchStatus.SWIPED_RIGHT,
    )
