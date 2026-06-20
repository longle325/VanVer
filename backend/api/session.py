"""
Session identity helpers for user-scoped API operations.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, Request, status

SESSION_USER_ID_KEY = "user_id"


def session_user_id(request: Request) -> UUID | None:
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


def require_authenticated_session_user(request: Request) -> UUID:
    user_id = session_user_id(request)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return user_id


def require_session_owner(request: Request, user_id: UUID) -> UUID:
    session_id = require_authenticated_session_user(request)
    if session_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated session does not match request user.",
        )
    return session_id
