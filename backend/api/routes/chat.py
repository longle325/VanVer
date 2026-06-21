"""
Character chat endpoint with SSE streaming.

POST /api/v1/chat/stream
  Opens a Server-Sent Events connection and streams the character's
  response token-by-token.

Pipeline:
  1. Validate user has matched with the character
  2. Codex agent searches knowledge_base/ for literary context
  3. System prompt assembled (character voice + context)
  4. LLM response streamed via SSE
"""

from __future__ import annotations

import json
import logging
from typing import Any, Awaitable, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from api.deps import get_chat, get_db
from api.session import session_user_id
from core.config import settings
from models.db_models import ChatRole, MatchStatus
from models.schemas import ChatHistoryResponse, ChatRequest, ChatMessageResponse
from services import db_postgres as db
from services.chat_service import ChatService
from services.chat_quota import ChatQuotaExceeded, enforce_monthly_chat_quota

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


async def _validate_chat_access(
    session: AsyncSession,
    user_id: UUID,
    character_id: UUID,
):
    user = await db.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    character = await db.get_character(session, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found.")

    match = await db.get_match(session, user_id, character_id)
    if not match or match.status == MatchStatus.SWIPED_LEFT:
        raise HTTPException(
            status_code=403,
            detail="You must match with this character before chatting.",
        )

    return user, character, match


def _resolve_chat_user_id(
    request: Request,
    requested_user_id: UUID | None,
) -> UUID:
    current_user_id = session_user_id(request)
    if current_user_id is not None:
        if requested_user_id is not None and requested_user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authenticated session does not match request user.",
            )
        return current_user_id

    if requested_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return requested_user_id


async def chat_event_generator(
    *,
    session: AsyncSession,
    chat_service: ChatService,
    user_id: UUID,
    character_id: UUID,
    character: Any,
    user_message: str,
    chat_history: list[dict[str, str]],
    create_chat_message: Callable[..., Awaitable[Any]] | None = None,
):
    yield {"event": "ready", "data": "{}"}

    create_message = create_chat_message or db.create_chat_message
    assistant_chunks: list[str] = []
    try:
        guardrail_response = chat_service.guardrail_response(
            character_slug=character.slug,
            character_name=character.name,
            user_message=user_message,
            chat_history=chat_history,
        )
        if guardrail_response:
            await create_message(
                session,
                user_id=user_id,
                character_id=character_id,
                role=ChatRole.USER,
                content=user_message,
            )
            assistant_chunks.append(guardrail_response)
            yield {"data": guardrail_response}
            await create_message(
                session,
                user_id=user_id,
                character_id=character_id,
                role=ChatRole.ASSISTANT,
                content=guardrail_response,
            )
            return

        retrieval = await chat_service.prepare_retrieval(
            character_slug=character.slug,
            character_name=character.name,
            user_message=user_message,
        )
        yield {
            "event": "sources",
            "data": json.dumps(
                {
                    "retrieval_mode": retrieval["retrieval_mode"],
                    "sources": retrieval["sources"],
                },
                ensure_ascii=False,
            ),
        }
        await create_message(
            session,
            user_id=user_id,
            character_id=character_id,
            role=ChatRole.USER,
            content=user_message,
        )
        async for chunk in chat_service.stream_response(
            character_slug=character.slug,
            character_name=character.name,
            user_message=user_message,
            voice_instructions=character.voice_instructions,
            chat_history=chat_history,
            retrieval=retrieval,
        ):
            assistant_chunks.append(chunk)
            yield {"data": chunk}
    except Exception as exc:
        logger.exception("Chat stream failed: %s", exc)
        yield {
            "event": "error",
            "data": json.dumps(
                {"error": str(exc)},
                ensure_ascii=False,
            ),
        }
        return

    assistant_message = "".join(assistant_chunks).strip()
    if assistant_message:
        await create_message(
            session,
            user_id=user_id,
            character_id=character_id,
            role=ChatRole.ASSISTANT,
            content=assistant_message,
        )


@router.get("/history", response_model=ChatHistoryResponse)
async def chat_history(
    user_id: UUID = Query(..., description="Current user's UUID"),
    character_id: UUID = Query(..., description="Character UUID"),
    limit: int = Query(100, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    await _validate_chat_access(session, user_id, character_id)
    messages = await db.list_chat_messages(
        session,
        user_id=user_id,
        character_id=character_id,
        limit=limit,
    )
    return ChatHistoryResponse(
        messages=[ChatMessageResponse.model_validate(message) for message in messages]
    )


@router.post("/stream")
async def chat_stream(
    request: Request,
    body: ChatRequest,
    session: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat),
):
    user_id = _resolve_chat_user_id(request, body.user_id)
    _, character, _ = await _validate_chat_access(
        session,
        user_id,
        body.character_id,
    )
    try:
        await enforce_monthly_chat_quota(
            session,
            user_id=user_id,
            character_id=body.character_id,
        )
    except ChatQuotaExceeded as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    recent_messages = await db.list_recent_chat_messages(
        session,
        user_id=user_id,
        character_id=body.character_id,
        limit=settings.CHAT_PROMPT_HISTORY_MAX_MESSAGES,
    )
    chat_history = [
        {"role": message.role.value, "content": message.content}
        for message in recent_messages
    ]

    return EventSourceResponse(
        chat_event_generator(
            session=session,
            chat_service=chat_service,
            user_id=user_id,
            character_id=body.character_id,
            character=character,
            user_message=body.message,
            chat_history=chat_history,
        )
    )
