"""
PostgreSQL data-access layer.

All database queries live here so route handlers stay thin.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.db_models import (
    Challenge,
    ChallengeAttempt,
    Character,
    CharacterEvent,
    CharacterRelationship,
    ChatMessage,
    ChatRole,
    Match,
    MatchStatus,
    User,
)
from services.oauth_service import OAuthProfile


# ── Users ─────────────────────────────────────────────────────────────────


async def create_user(db: AsyncSession, username: str, grade_level: int) -> User:
    user = User(username=username, grade_level=grade_level)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_oauth_identity(
    db: AsyncSession, provider: str, subject: str
) -> Optional[User]:
    result = await db.execute(
        select(User).where(
            User.auth_provider == provider,
            User.auth_subject == subject,
        )
    )
    return result.scalar_one_or_none()


async def upsert_oauth_user(db: AsyncSession, profile: OAuthProfile) -> User:
    """
    Create or update a user from a verified OAuth/OIDC provider identity.

    The stable account key is provider + subject. Email is profile data, not
    the primary identity, because email can change and is not universal.
    """
    now = datetime.now(timezone.utc)
    user = await get_user_by_oauth_identity(db, profile.provider, profile.subject)
    if user:
        user.email = profile.email
        user.display_name = profile.display_name
        user.last_login_at = now
        await db.commit()
        await db.refresh(user)
        return user

    username = await _unique_username(db, profile.username_seed)
    user = User(
        username=username,
        grade_level=10,
        email=profile.email,
        display_name=profile.display_name,
        auth_provider=profile.provider,
        auth_subject=profile.subject,
        last_login_at=now,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def add_points(db: AsyncSession, user_id: UUID, points: int) -> int:
    """Add *points* to a user's total_score and return the new total."""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(total_score=User.total_score + points)
    )
    await db.commit()
    user = await get_user(db, user_id)
    return user.total_score if user else 0


async def _unique_username(db: AsyncSession, seed: str) -> str:
    base = (seed or "oauth-user")[:50]
    candidate = base
    suffix = 2
    while await get_user_by_username(db, candidate):
        suffix_text = f"-{suffix}"
        candidate = f"{base[: 50 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return candidate


# ── Characters ────────────────────────────────────────────────────────────


async def get_character(db: AsyncSession, character_id: UUID) -> Optional[Character]:
    return await db.get(Character, character_id)


async def get_character_by_slug(db: AsyncSession, slug: str) -> Optional[Character]:
    result = await db.execute(select(Character).where(Character.slug == slug))
    return result.scalar_one_or_none()


async def get_unswiped_characters(
    db: AsyncSession, user_id: UUID, limit: int = 10
) -> List[Character]:
    """Return characters the user has NOT swiped on yet."""
    swiped_ids = select(Match.character_id).where(Match.user_id == user_id)
    result = await db.execute(
        select(Character).where(Character.id.notin_(swiped_ids)).limit(limit)
    )
    return list(result.scalars().all())


async def list_characters(db: AsyncSession) -> List[Character]:
    result = await db.execute(select(Character))
    return list(result.scalars().all())


async def list_character_relationships(
    db: AsyncSession,
    character_id: UUID,
) -> List[CharacterRelationship]:
    result = await db.execute(
        select(CharacterRelationship).where(
            CharacterRelationship.character_id == character_id
        )
    )
    return list(result.scalars().all())


async def list_character_events(
    db: AsyncSession,
    character_id: UUID,
) -> List[CharacterEvent]:
    result = await db.execute(
        select(CharacterEvent)
        .where(CharacterEvent.character_id == character_id)
        .order_by(CharacterEvent.sequence_number.asc())
    )
    return list(result.scalars().all())


# ── Matches ───────────────────────────────────────────────────────────────


async def create_match(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
    status: MatchStatus = MatchStatus.SWIPED_RIGHT,
) -> Match:
    match = Match(
        user_id=user_id,
        character_id=character_id,
        status=status,
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match


async def get_match(
    db: AsyncSession, user_id: UUID, character_id: UUID
) -> Optional[Match]:
    result = await db.execute(
        select(Match).where(
            Match.user_id == user_id,
            Match.character_id == character_id,
        )
    )
    return result.scalar_one_or_none()


async def update_match_status(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
    status: MatchStatus,
) -> Optional[Match]:
    await db.execute(
        update(Match)
        .where(Match.user_id == user_id, Match.character_id == character_id)
        .values(status=status)
    )
    await db.commit()
    return await get_match(db, user_id, character_id)


async def get_user_matches(
    db: AsyncSession,
    user_id: UUID,
    statuses: Optional[Iterable[MatchStatus]] = None,
) -> List[Match]:
    stmt = (
        select(Match)
        .options(selectinload(Match.character))
        .where(Match.user_id == user_id)
    )
    if statuses is not None:
        stmt = stmt.where(Match.status.in_(list(statuses)))
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ── Challenges ────────────────────────────────────────────────────────────


async def get_challenge_for_character(
    db: AsyncSession, character_id: UUID
) -> Optional[Challenge]:
    result = await db.execute(
        select(Challenge).where(Challenge.character_id == character_id)
    )
    return result.scalar_one_or_none()


async def get_challenge_attempt(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
) -> Optional[ChallengeAttempt]:
    result = await db.execute(
        select(ChallengeAttempt).where(
            ChallengeAttempt.user_id == user_id,
            ChallengeAttempt.character_id == character_id,
        )
    )
    return result.scalar_one_or_none()


async def create_challenge_attempt(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
    answers: list[int],
    score: int,
    total: int,
    passed: bool,
    points_earned: int,
    explanations: list[str],
) -> ChallengeAttempt:
    attempt = ChallengeAttempt(
        user_id=user_id,
        character_id=character_id,
        answers=answers,
        score=score,
        total=total,
        passed=passed,
        points_earned=points_earned,
        explanations=explanations,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return attempt


# ── Chat messages ─────────────────────────────────────────────────────────


async def create_chat_message(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
    role: ChatRole,
    content: str,
) -> ChatMessage:
    message = ChatMessage(
        user_id=user_id,
        character_id=character_id,
        role=role,
        content=content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def list_chat_messages(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
    limit: int = 100,
) -> List[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.user_id == user_id,
            ChatMessage.character_id == character_id,
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_recent_chat_messages(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
    limit: int = 8,
) -> List[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.user_id == user_id,
            ChatMessage.character_id == character_id,
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    return list(reversed(messages))


# ── Leaderboard ───────────────────────────────────────────────────────────


async def get_leaderboard(db: AsyncSession, limit: int = 50) -> List[dict]:
    """
    Return top users ranked by total_score.

    Each row includes the count of CHALLENGE_PASSED matches as
    `characters_unlocked`.
    """
    unlocked_count = (
        select(
            Match.user_id,
            func.count(Match.id).label("characters_unlocked"),
        )
        .where(Match.status == MatchStatus.CHALLENGE_PASSED)
        .group_by(Match.user_id)
        .subquery()
    )

    stmt = (
        select(
            User.id.label("user_id"),
            User.username,
            User.total_score,
            func.coalesce(unlocked_count.c.characters_unlocked, 0).label(
                "characters_unlocked"
            ),
        )
        .outerjoin(unlocked_count, User.id == unlocked_count.c.user_id)
        .order_by(User.total_score.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "rank": idx + 1,
            "user_id": row.user_id,
            "username": row.username,
            "total_score": row.total_score,
            "characters_unlocked": row.characters_unlocked,
        }
        for idx, row in enumerate(rows)
    ]
