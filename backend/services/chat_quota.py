"""Monthly chat quota enforcement for free-tier users."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from services import db_postgres as db


class ChatQuotaExceeded(Exception):
    """Raised when a chat request would exceed the configured free quota."""

    status_code = 402

    def __init__(
        self,
        *,
        limit_type: str,
        limit: int,
        used: int,
        reset_at: datetime,
    ):
        self.detail = {
            "error": "chat_quota_exceeded",
            "limit_type": limit_type,
            "limit": limit,
            "used": used,
            "reset_at": reset_at.isoformat(),
            "upgrade_required": True,
            "billing_plan": "free",
        }
        super().__init__(str(self.detail))


def month_start_utc(now: Optional[datetime] = None) -> datetime:
    """Return the UTC month boundary used for quota reset."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    return current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def next_month_start_utc(month_start: datetime) -> datetime:
    year = month_start.year
    month = month_start.month
    if month == 12:
        return month_start.replace(year=year + 1, month=1)
    return month_start.replace(month=month + 1)


async def enforce_monthly_chat_quota(
    session: AsyncSession,
    *,
    user_id: UUID,
    character_id: UUID,
    now: Optional[datetime] = None,
    character_limit: Optional[int] = None,
    messages_per_character_limit: Optional[int] = None,
) -> None:
    """
    Enforce the free-tier monthly chat quota.

    Limits are based on persisted user chat messages, which keeps reset logic
    simple and leaves a durable usage trail for a future billing layer.
    """
    resolved_character_limit = (
        settings.CHAT_MONTHLY_CHARACTER_LIMIT
        if character_limit is None
        else character_limit
    )
    resolved_message_limit = (
        settings.CHAT_MONTHLY_MESSAGES_PER_CHARACTER_LIMIT
        if messages_per_character_limit is None
        else messages_per_character_limit
    )
    if resolved_character_limit < 1 and resolved_message_limit < 1:
        return

    since = month_start_utc(now)
    reset_at = next_month_start_utc(since)
    usage = await db.get_monthly_chat_quota_usage(
        session,
        user_id=user_id,
        character_id=character_id,
        since=since,
    )
    used_characters = int(usage["used_characters"])
    messages_for_character = int(usage["messages_for_character"])

    if (
        resolved_character_limit > 0
        and messages_for_character == 0
        and used_characters >= resolved_character_limit
    ):
        raise ChatQuotaExceeded(
            limit_type="monthly_character_limit",
            limit=resolved_character_limit,
            used=used_characters,
            reset_at=reset_at,
        )

    if (
        resolved_message_limit > 0
        and messages_for_character >= resolved_message_limit
    ):
        raise ChatQuotaExceeded(
            limit_type="monthly_messages_per_character_limit",
            limit=resolved_message_limit,
            used=messages_for_character,
            reset_at=reset_at,
        )
