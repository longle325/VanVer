"""
Chat orchestration service.

Implements the simplified pipeline (Codex replaces GraphRAG):

  1. Receive user message
  2. Codex agent searches knowledge_base/ for relevant literary context
  3. Assemble system prompt  (character voice + retrieved context)
  4. Stream LLM response token-by-token via an async generator

The route layer wraps the generator in an SSE EventSourceResponse.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Optional

from openai import AsyncOpenAI

from core.config import settings
from core.prompt_templates import build_character_prompt
from services.chat_guardrails import (
    evaluate_chat_guardrail,
    evaluate_chat_guardrail_hard_rules,
    off_topic_guardrail_result,
    should_defer_to_llm_guardrail,
)
from services.codex_agent import CodexKnowledgeAgent
from services.knowledge_retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)


_GUARDRAIL_CLASSIFIER_INSTRUCTIONS = """
You classify whether a student message is allowed in a Vietnamese literature
character chat.

Allowed:
- Questions about the selected character's life, actions, emotions, motives,
  relationships, choices, fate, or character arc in the literary work.
- Questions about the author, work, plot, canon details, themes, conflicts,
  symbols, literary analysis, or classroom interpretation of the work.
- Natural follow-ups that depend on the existing conversation.

Blocked:
- Math, coding, current events, weather, prices, pop culture, jokes, memes, or
  everyday advice unrelated to the selected author/work/character.
- Personal-preference questions not grounded in the work, such as favorite food
  or modern celebrities.
- Requests to roleplay as a different character or speak another character's
  lines.

Return only the JSON object required by the schema. When uncertain, allow only
if the message can reasonably be answered from the selected literary work or
the selected character's lived experience inside that work.
""".strip()

_GUARDRAIL_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "name": "chat_guardrail_decision",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "decision": {
                "type": "string",
                "enum": ["allow", "block"],
            },
            "reason": {
                "type": "string",
                "enum": [
                    "character_or_work_question",
                    "character_life_or_arc",
                    "follow_up",
                    "off_topic",
                    "other_character_voice",
                ],
            },
        },
        "required": ["decision", "reason"],
    },
}


class ChatService:
    """Orchestrates context retrieval + LLM streaming for character chat."""

    def __init__(
        self,
        codex_agent: Optional[CodexKnowledgeAgent],
        knowledge_retriever: Optional[KnowledgeRetriever] = None,
        openai_client: Optional[AsyncOpenAI] = None,
        chat_model: Optional[str] = None,
    ):
        self.codex = codex_agent
        self.retriever = knowledge_retriever
        self.client = openai_client or AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )
        self.chat_model = chat_model or settings.CHAT_MODEL

    # ------------------------------------------------------------------
    # Public streaming API
    # ------------------------------------------------------------------
    async def stream_response(
        self,
        character_slug: str,
        character_name: str,
        user_message: str,
        voice_instructions: Optional[str] = None,
        chat_history: Optional[list[dict[str, str]]] = None,
        retrieval: Optional[dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        Yield streamed text chunks for a character chat turn.

        Parameters
        ----------
        character_slug : str
            e.g. "chi_pheo"
        character_name : str
            e.g. "Chí Phèo"
        user_message : str
            The student's question.
        voice_instructions : str | None
            Per-character prompt override (from DB).
        """
        if retrieval is None:
            guardrail_response = await self.guardrail_response(
                character_slug=character_slug,
                character_name=character_name,
                user_message=user_message,
                chat_history=chat_history,
            )
            if guardrail_response:
                yield guardrail_response
                return

        # Step 1 — retrieve character-scoped literary context.
        retrieval = retrieval or await self.prepare_retrieval(
            character_slug=character_slug,
            character_name=character_name,
            user_message=user_message,
        )

        # Step 2 — build the system prompt
        system_prompt = build_character_prompt(
            character_slug=character_slug,
            character_name=character_name,
            retrieved_context=retrieval["context"],
            voice_instructions=voice_instructions,
            conversation_context=self._format_chat_history(chat_history or []),
            user_message=user_message,
        )

        # Step 3 — stream the LLM response
        if self._uses_responses_api():
            stream = await self.client.responses.create(
                **self._responses_kwargs(system_prompt, user_message)
            )
            async for event in stream:
                delta = self._response_event_delta(event)
                if delta:
                    yield delta
            return

        stream = await self.client.chat.completions.create(
            **self._completion_kwargs(system_prompt, user_message)
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    def _uses_responses_api(self) -> bool:
        return self.chat_model.startswith(("gpt-5.4", "gpt-5.5"))

    async def guardrail_response(
        self,
        *,
        character_slug: Optional[str] = None,
        character_name: str,
        user_message: str,
        chat_history: Optional[list[dict[str, str]]] = None,
    ) -> Optional[str]:
        hard_result = evaluate_chat_guardrail_hard_rules(
            user_message,
            character_name=character_name,
        )
        if hard_result:
            return hard_result.response

        should_classify = (
            settings.CHAT_GUARDRAIL_LLM_ENABLED
            and should_defer_to_llm_guardrail(
                user_message,
                character_name=character_name,
                character_slug=character_slug,
                has_chat_history=bool(chat_history),
            )
        )
        if should_classify:
            decision = await self._llm_guardrail_decision(
                character_slug=character_slug,
                character_name=character_name,
                user_message=user_message,
                chat_history=chat_history,
            )
            if decision == "block":
                return off_topic_guardrail_result(character_name).response
            return None

        result = evaluate_chat_guardrail(
            user_message,
            character_name=character_name,
            character_slug=character_slug,
            has_chat_history=bool(chat_history),
        )
        return result.response if result else None

    async def _llm_guardrail_decision(
        self,
        *,
        character_slug: Optional[str],
        character_name: str,
        user_message: str,
        chat_history: Optional[list[dict[str, str]]] = None,
    ) -> Optional[str]:
        classifier_input = {
            "selected_character": character_name,
            "character_slug": character_slug,
            "has_chat_history": bool(chat_history),
            "recent_history": self._format_chat_history(
                chat_history or [],
                max_messages=4,
                max_chars_per_message=300,
                max_total_chars=900,
            ),
            "student_message": user_message,
        }
        try:
            response = await asyncio.wait_for(
                self.client.responses.create(
                    model=settings.CHAT_GUARDRAIL_MODEL,
                    instructions=_GUARDRAIL_CLASSIFIER_INSTRUCTIONS,
                    input=json.dumps(classifier_input, ensure_ascii=False),
                    reasoning={"effort": "none"},
                    text={"format": _GUARDRAIL_RESPONSE_FORMAT},
                    store=False,
                ),
                timeout=settings.CHAT_GUARDRAIL_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            logger.warning("Chat guardrail classifier failed: %s", exc)
            return None

        try:
            payload = json.loads(self._response_output_text(response))
        except (TypeError, ValueError) as exc:
            logger.warning("Chat guardrail classifier returned invalid JSON: %s", exc)
            return None

        decision = payload.get("decision")
        if decision in {"allow", "block"}:
            return decision
        return None

    def _responses_kwargs(
        self,
        system_prompt: str,
        user_message: str,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.chat_model,
            "instructions": system_prompt,
            "input": user_message,
            "stream": True,
        }
        if settings.CHAT_REASONING_EFFORT:
            kwargs["reasoning"] = {"effort": settings.CHAT_REASONING_EFFORT}
        if settings.CHAT_RESPONSE_VERBOSITY:
            kwargs["text"] = {"verbosity": settings.CHAT_RESPONSE_VERBOSITY}
        return kwargs

    @staticmethod
    def _response_event_delta(event: Any) -> Optional[str]:
        if isinstance(event, dict):
            if event.get("type") == "response.output_text.delta":
                return event.get("delta") or None
            return None

        if getattr(event, "type", None) == "response.output_text.delta":
            return getattr(event, "delta", None) or None
        return None

    @staticmethod
    def _response_output_text(response: Any) -> str:
        if isinstance(response, dict):
            output_text = response.get("output_text")
            if output_text:
                return str(output_text)
            output = response.get("output") or []
        else:
            output_text = getattr(response, "output_text", None)
            if output_text:
                return str(output_text)
            output = getattr(response, "output", []) or []

        parts: list[str] = []
        for item in output:
            content = item.get("content", []) if isinstance(item, dict) else getattr(item, "content", [])
            for block in content or []:
                if isinstance(block, dict):
                    text = block.get("text")
                else:
                    text = getattr(block, "text", None)
                if text:
                    parts.append(str(text))
        return "".join(parts)

    async def prepare_retrieval(
        self,
        character_slug: str,
        character_name: str,
        user_message: str,
    ) -> dict[str, Any]:
        if self.retriever is not None:
            if hasattr(self.retriever, "search_with_sources_async"):
                result = await self.retriever.search_with_sources_async(
                    character_slug,
                    user_message,
                )
                if result.get("context"):
                    return result
            if hasattr(self.retriever, "search_context_async"):
                context = await self.retriever.search_context_async(
                    character_slug,
                    user_message,
                )
            else:
                context = self.retriever.search_context(character_slug, user_message)
            if context:
                return {
                    "context": context,
                    "sources": [],
                    "retrieval_mode": "legacy",
                }

        if self.codex is not None:
            context = await self.codex.search_context(character_name, user_message)
            if context:
                return {
                    "context": context,
                    "sources": [],
                    "retrieval_mode": "codex",
                }

        return {
            "context": (
                "(No specific context was found in the knowledge base. "
                "Answer from general canon knowledge about the character.)"
            ),
            "sources": [],
            "retrieval_mode": "none",
        }

    def _completion_kwargs(
        self,
        system_prompt: str,
        user_message: str,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": True,
        }

        if self.chat_model.startswith(("gpt-5", "o1", "o3", "o4")):
            return kwargs

        kwargs["temperature"] = 0.7
        return kwargs

    @staticmethod
    def _format_chat_history(
        chat_history: list[dict[str, str]],
        *,
        max_messages: Optional[int] = None,
        max_chars_per_message: Optional[int] = None,
        max_total_chars: Optional[int] = None,
    ) -> str:
        resolved_max_messages = (
            settings.CHAT_PROMPT_HISTORY_MAX_MESSAGES
            if max_messages is None
            else max_messages
        )
        resolved_max_chars = (
            settings.CHAT_PROMPT_HISTORY_MAX_CHARS_PER_MESSAGE
            if max_chars_per_message is None
            else max_chars_per_message
        )
        resolved_max_total = (
            settings.CHAT_PROMPT_HISTORY_MAX_TOTAL_CHARS
            if max_total_chars is None
            else max_total_chars
        )
        if resolved_max_messages <= 0:
            return ""

        lines: list[str] = []
        for message in chat_history[-resolved_max_messages:]:
            content = message.get("content", "").strip()
            if not content:
                continue
            if resolved_max_chars > 0 and len(content) > resolved_max_chars:
                content = f"{content[:resolved_max_chars].rstrip()}... [truncated]"
            role = message.get("role")
            label = "Character" if role == "assistant" else "Student"
            lines.append(f"{label}: {content}")

        while lines and resolved_max_total > 0:
            formatted = "\n".join(lines)
            if len(formatted) <= resolved_max_total:
                return formatted
            lines.pop(0)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Factory (used by deps.py)
# ---------------------------------------------------------------------------
_service: Optional[ChatService] = None


def get_chat_service(
    codex_agent: Optional[CodexKnowledgeAgent],
    knowledge_retriever: Optional[KnowledgeRetriever] = None,
) -> ChatService:
    global _service
    if _service is None:
        _service = ChatService(
            codex_agent=codex_agent,
            knowledge_retriever=knowledge_retriever,
        )
    return _service
