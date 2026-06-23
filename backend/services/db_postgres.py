"""
PostgreSQL data-access layer.

All database queries live here so route handlers stay thin.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
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
    UserProgress,
)
from services.oauth_service import OAuthProfile


UNLOCKED_MATCH_STATUSES = (
    MatchStatus.SWIPED_RIGHT,
    MatchStatus.CHAT_UNLOCKED,
    MatchStatus.CHALLENGE_PASSED,
)


# Fields inside a level_results slot that only the server may write. The grade
# endpoint sets them and progress saves preserve them (see upsert_user_progress
# and _merge_server_owned_level_fields). This keeps both the score and the
# server-graded progression authoritative — a client save can't forge a pass or
# revert a server-graded retake.
SERVER_OWNED_LEVEL_FIELDS = ("server_points", "score", "total", "passed")


def calculate_progress_points(level_results: dict | None) -> int:
    """Sum server-graded level points from level_results.

    Only the server-written ``server_points`` field is trusted; client-supplied
    scores are ignored. The grade endpoint writes this field server-side and
    progress saves preserve it, so this stays authoritative.
    """
    if not isinstance(level_results, dict):
        return 0

    total = 0
    for character_results in level_results.values():
        if not isinstance(character_results, dict):
            continue
        for result in character_results.values():
            if not isinstance(result, dict):
                continue
            points = result.get("server_points")
            if isinstance(points, bool):
                continue
            if isinstance(points, (int, float)):
                total += int(points)
    return total


def _merge_server_owned_level_fields(incoming: dict | None, existing: dict | None) -> dict:
    """Merge a client-supplied level_results blob with the stored one so that
    server-owned fields are never lost or forged.

    For each (character, level) slot: take the client's display fields but
    strip any client-supplied server-owned fields and restore the server-owned
    values from the stored row. Slots the client omits are kept as-is from the
    stored row so a partial sync can't drop server scores.
    """
    incoming = incoming if isinstance(incoming, dict) else {}
    existing = existing if isinstance(existing, dict) else {}
    merged: dict = {}

    for slug in set(incoming) | set(existing):
        in_char = incoming.get(slug)
        ex_char = existing.get(slug)
        in_char = in_char if isinstance(in_char, dict) else {}
        ex_char = ex_char if isinstance(ex_char, dict) else {}
        merged_char: dict = {}

        for level_key in set(in_char) | set(ex_char):
            in_slot = in_char.get(level_key)
            ex_slot = ex_char.get(level_key)
            in_slot = in_slot if isinstance(in_slot, dict) else None
            ex_slot = ex_slot if isinstance(ex_slot, dict) else None

            if in_slot is None and ex_slot is None:
                continue
            if in_slot is None:
                merged_char[level_key] = dict(ex_slot)
                continue

            slot = dict(in_slot)
            for field in SERVER_OWNED_LEVEL_FIELDS:
                slot.pop(field, None)
            if ex_slot is not None:
                for field in SERVER_OWNED_LEVEL_FIELDS:
                    if field in ex_slot:
                        slot[field] = ex_slot[field]
            merged_char[level_key] = slot

        merged[slug] = merged_char

    return merged


async def get_effective_total_score(db: AsyncSession, user: User) -> int:
    """Combine persisted account score with synced level challenge awards."""
    progress = await get_user_progress(db, user.id)
    progress_points = calculate_progress_points(
        progress.level_results if progress is not None else None
    )
    return int(user.total_score or 0) + progress_points


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


async def update_user_display_name(
    db: AsyncSession,
    user_id: UUID,
    display_name: str,
) -> Optional[User]:
    user = await get_user(db, user_id)
    if user is None:
        return None
    user.display_name = display_name
    await db.commit()
    await db.refresh(user)
    return user


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


# ── User progress ─────────────────────────────────────────────────────────


async def get_user_progress(
    db: AsyncSession,
    user_id: UUID,
    *,
    for_update: bool = False,
) -> Optional[UserProgress]:
    stmt = select(UserProgress).where(UserProgress.user_id == user_id)
    if for_update:
        # Serialize concurrent read-modify-write of the JSON blob (a level
        # award racing the debounced progress autosave) so neither clobbers
        # the other's server_points.
        stmt = stmt.with_for_update()
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_or_create_progress_locked(
    db: AsyncSession, user_id: UUID, now: datetime
) -> UserProgress:
    """Return the user's progress row locked FOR UPDATE, creating it if absent.

    Closes the first-write race: FOR UPDATE locks nothing when the row does not
    exist, so two concurrent first writes could both try to INSERT the same
    user_id. If a concurrent insert wins, retry the locked fetch instead of
    failing with an IntegrityError.
    """
    progress = await get_user_progress(db, user_id, for_update=True)
    if progress is not None:
        return progress
    progress = UserProgress(
        user_id=user_id,
        completed={},
        level_results={},
        updated_at=now,
    )
    db.add(progress)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        progress = await get_user_progress(db, user_id, for_update=True)
        if progress is None:
            raise
    return progress


async def upsert_user_progress(
    db: AsyncSession,
    user_id: UUID,
    completed: dict,
    level_results: dict,
) -> UserProgress:
    now = datetime.now(timezone.utc)
    progress = await _get_or_create_progress_locked(db, user_id, now)
    existing_level_results = (
        progress.level_results if isinstance(progress.level_results, dict) else {}
    )
    # A client save may not carry server-graded fields (and must not be
    # trusted to set them), so merge them back from the stored row.
    merged_level_results = _merge_server_owned_level_fields(
        level_results, existing_level_results
    )
    progress.completed = completed
    progress.level_results = merged_level_results
    progress.updated_at = now

    await db.commit()
    await db.refresh(progress)
    return progress


async def record_level_award(
    db: AsyncSession,
    user_id: UUID,
    character_slug: str,
    level: int,
    points: int,
    *,
    score: int,
    total: int,
    passed: bool,
) -> UserProgress:
    """Write the server-graded result for one (character, level) into the
    user's level_results. Idempotent: a retake overwrites the prior award for
    that slot, so totals never double-count.

    Persists the server-graded score/total/passed in the same commit as the
    award so progression stays consistent even if the client's separate
    progress save never lands.
    """
    now = datetime.now(timezone.utc)
    progress = await _get_or_create_progress_locked(db, user_id, now)
    base = dict(progress.level_results) if isinstance(progress.level_results, dict) else {}
    character_levels = base.get(character_slug)
    character_levels = dict(character_levels) if isinstance(character_levels, dict) else {}
    level_key = str(level)
    slot = character_levels.get(level_key)
    slot = dict(slot) if isinstance(slot, dict) else {}
    slot["server_points"] = int(points)
    slot["score"] = int(score)
    slot["total"] = int(total)
    slot["passed"] = bool(passed)
    character_levels[level_key] = slot
    base[character_slug] = character_levels

    progress.level_results = base
    progress.updated_at = now

    await db.commit()
    await db.refresh(progress)
    return progress


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


async def delete_left_swipes(db: AsyncSession, user_id: UUID) -> int:
    """Delete the user's left-swipe (skip) records, leaving real matches intact.

    The discovery deck is computed from Match rows (a character with any Match
    row is excluded), so clearing a user's SWIPED_LEFT rows is what actually
    makes skipped cards reappear. SWIPED_RIGHT rows are never touched.

    Returns the number of skip records removed.
    """
    result = await db.execute(
        delete(Match).where(
            Match.user_id == user_id,
            Match.status == MatchStatus.SWIPED_LEFT,
        )
    )
    await db.commit()
    return result.rowcount or 0


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


async def get_monthly_chat_quota_usage(
    db: AsyncSession,
    user_id: UUID,
    character_id: UUID,
    since: datetime,
) -> dict[str, int]:
    base_filters = (
        ChatMessage.user_id == user_id,
        ChatMessage.role == ChatRole.USER,
        ChatMessage.created_at >= since,
    )
    used_characters_result = await db.execute(
        select(func.count(func.distinct(ChatMessage.character_id))).where(
            *base_filters
        )
    )
    messages_for_character_result = await db.execute(
        select(func.count(ChatMessage.id)).where(
            *base_filters,
            ChatMessage.character_id == character_id,
        )
    )

    return {
        "used_characters": int(used_characters_result.scalar_one() or 0),
        "messages_for_character": int(
            messages_for_character_result.scalar_one() or 0
        ),
    }


# ── Leaderboard ───────────────────────────────────────────────────────────


async def get_leaderboard(db: AsyncSession, limit: int = 50) -> List[dict]:
    """
    Return top users ranked by effective total score.

    Each row includes the count of matched/unlocked characters as
    `characters_unlocked`. Left-swiped characters are intentionally excluded.
    Level challenge progress is synced into user_progress rather than legacy
    challenge_attempts, so include those awards in the displayed score.
    """
    unlocked_count = (
        select(
            Match.user_id,
            func.count(Match.id).label("characters_unlocked"),
        )
        .where(Match.status.in_(UNLOCKED_MATCH_STATUSES))
        .group_by(Match.user_id)
        .subquery()
    )

    stmt = (
        select(
            User.id.label("user_id"),
            User.username,
            User.display_name,
            User.total_score,
            UserProgress.level_results,
            func.coalesce(unlocked_count.c.characters_unlocked, 0).label(
                "characters_unlocked"
            ),
        )
        .outerjoin(unlocked_count, User.id == unlocked_count.c.user_id)
        .outerjoin(UserProgress, User.id == UserProgress.user_id)
    )

    result = await db.execute(stmt)
    rows = result.all()
    display_names = {}
    for row in rows:
        display_name = (row.display_name or "").strip()
        display_names[row.user_id] = display_name or row.username
    ranked = sorted(
        rows,
        key=lambda row: (
            -(
                int(row.total_score or 0)
                + calculate_progress_points(row.level_results)
            ),
            display_names[row.user_id].lower(),
        ),
    )[:limit]

    return [
        {
            "rank": idx + 1,
            "user_id": row.user_id,
            "username": display_names[row.user_id],
            "total_score": int(row.total_score or 0)
            + calculate_progress_points(row.level_results),
            "characters_unlocked": row.characters_unlocked,
        }
        for idx, row in enumerate(ranked)
    ]
