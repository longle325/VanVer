from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from openai import AsyncOpenAI
    from services.knowledge_retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)


class OpenEndedGradingError(RuntimeError):
    """Raised when the LLM grader cannot produce a usable rubric verdict."""


class OpenEndedGradingService:
    """Grades one open-ended challenge answer with RAG context and a rubric."""

    def __init__(
        self,
        knowledge_retriever: Optional["KnowledgeRetriever"] = None,
        openai_client: Optional["AsyncOpenAI"] = None,
        chat_model: Optional[str] = None,
    ):
        self.retriever = knowledge_retriever
        config = None
        if openai_client is None or chat_model is None:
            from core.config import settings as config

        if openai_client is None:
            from openai import AsyncOpenAI

            openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.client = openai_client
        self.chat_model = chat_model if chat_model is not None else config.CHAT_MODEL

    async def grade(
        self,
        *,
        character_slug: str,
        character_name: str,
        work_title: str | None,
        phase_title: str | None,
        question: str,
        answer: str,
        rubric: str,
        evidence: str | None = None,
    ) -> dict[str, Any]:
        answer = answer.strip()
        if not answer:
            return {
                "score": 0,
                "passed": False,
                "feedback": "Câu trả lời còn trống.",
                "matched_criteria": [],
                "missing_criteria": ["Cần trả lời theo rubric."],
                "confidence": 1.0,
                "retrieval_mode": "none",
                "sources": [],
            }

        normalized_slug = character_slug.replace("-", "_")
        retrieval = await self._retrieve_context(
            normalized_slug,
            " ".join(part for part in [question, rubric, evidence or ""] if part),
        )
        payload = await self._call_grader(
            character_name=character_name,
            work_title=work_title,
            phase_title=phase_title,
            question=question,
            answer=answer,
            rubric=rubric,
            evidence=evidence,
            retrieved_context=retrieval["context"],
        )

        return {
            "score": 1 if int(payload.get("score", 0)) == 1 else 0,
            "passed": bool(payload.get("passed", payload.get("score") == 1)),
            "feedback": str(payload.get("feedback", "")).strip(),
            "matched_criteria": self._string_list(payload.get("matched_criteria")),
            "missing_criteria": self._string_list(payload.get("missing_criteria")),
            "confidence": self._confidence(payload.get("confidence")),
            "retrieval_mode": retrieval["retrieval_mode"],
            "sources": retrieval["sources"],
        }

    async def _retrieve_context(
        self,
        character_slug: str,
        query: str,
    ) -> dict[str, Any]:
        if self.retriever is None:
            return {"context": "", "sources": [], "retrieval_mode": "none"}

        result = await self.retriever.search_with_sources_async(character_slug, query)
        return {
            "context": result.get("context", ""),
            "sources": result.get("sources", []),
            "retrieval_mode": result.get("retrieval_mode", "none"),
        }

    async def _call_grader(
        self,
        *,
        character_name: str,
        work_title: str | None,
        phase_title: str | None,
        question: str,
        answer: str,
        rubric: str,
        evidence: str | None,
        retrieved_context: str,
    ) -> dict[str, Any]:
        try:
            response = await self.client.chat.completions.create(
                **self._completion_kwargs(
                    self._system_prompt(retrieved_context),
                    self._user_prompt(
                        character_name=character_name,
                        work_title=work_title,
                        phase_title=phase_title,
                        question=question,
                        answer=answer,
                        rubric=rubric,
                        evidence=evidence,
                    ),
                )
            )
        except Exception as exc:
            from openai import OpenAIError

            if not isinstance(exc, OpenAIError):
                raise
            logger.warning("Open-ended grader request failed: %s", exc)
            raise OpenEndedGradingError("Open-ended grader request failed.") from exc

        content = response.choices[0].message.content or ""
        try:
            return self._parse_json_object(content)
        except ValueError as exc:
            logger.warning("Open-ended grader returned invalid JSON: %s", content)
            raise OpenEndedGradingError("Open-ended grader returned invalid JSON.") from exc

    def _completion_kwargs(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        if self.chat_model.startswith(("gpt-5", "o1", "o3", "o4")):
            kwargs["max_completion_tokens"] = 2048
        else:
            kwargs["temperature"] = 0
            kwargs["max_tokens"] = 1000
        return kwargs

    @staticmethod
    def _system_prompt(retrieved_context: str) -> str:
        context = retrieved_context.strip() or "(Không có ngữ cảnh truy xuất.)"
        return f"""
Bạn là giám khảo Ngữ văn THPT. Nhiệm vụ: chấm MỘT câu trả lời tự luận ngắn theo rubric.

Quy tắc chấm bắt buộc:
1. Chỉ trả về JSON hợp lệ, không markdown, không giải thích ngoài JSON.
2. Điểm là nhị phân: score = 1 hoặc 0.
3. Không chấm theo cảm xúc, độ dài, văn hay, hay việc dùng đúng từ khóa rời rạc.
4. Chấp nhận diễn đạt khác, lỗi chính tả nhỏ, hoặc câu ngắn nếu ý nghĩa đúng.
5. Nếu rubric ghi "ít nhất N ý", yêu cầu tối thiểu N ý đúng.
6. Nếu rubric không ghi số lượng tối thiểu, xem rubric là các gợi ý ý chính, không phải danh sách từ khóa bắt buộc. Cho score = 1 khi câu trả lời nêu đúng ý trung tâm của câu hỏi hoặc đạt khoảng một nửa số ý lớn theo cách diễn đạt tương đương, miễn là không hiểu sai nghiêm trọng.
7. Không bắt buộc câu trả lời phải nêu đủ mọi chi tiết phụ như tên sự kiện, dẫn chứng, hoặc cách diễn đạt y hệt rubric nếu quan hệ nguyên nhân-kết quả chính đã rõ. Đừng trừ điểm chỉ vì thiếu một ý phụ khi câu trả lời đã cho thấy học sinh hiểu đúng mâu thuẫn/nguyên nhân chính.
8. Nếu câu trả lời chỉ nhắc một từ khóa mơ hồ, lạc đề, hoặc có hiểu sai nghiêm trọng về văn bản/tình tiết, score = 0.
9. Dùng ngữ cảnh truy xuất để kiểm tra tính đúng văn bản, nhưng ưu tiên đánh giá mức hiểu ý, không bắt học thuộc rubric.
10. feedback chỉ một câu ngắn: giải thích vì sao đạt hoặc chưa đạt, không liệt kê lại toàn bộ rubric.
11. Giữ JSON thật gọn: feedback tối đa 25 từ; matched_criteria và missing_criteria mỗi mảng tối đa 3 mục, mỗi mục tối đa 12 từ.

JSON schema:
{{
  "score": 0,
  "passed": false,
  "feedback": "Một câu tiếng Việt ngắn giải thích vì sao đạt hoặc chưa đạt.",
  "matched_criteria": ["tiêu chí đã đạt"],
  "missing_criteria": ["tiêu chí còn thiếu hoặc sai"],
  "confidence": 0.0
}}

Ngữ cảnh truy xuất:
{context}
""".strip()

    @staticmethod
    def _user_prompt(
        *,
        character_name: str,
        work_title: str | None,
        phase_title: str | None,
        question: str,
        answer: str,
        rubric: str,
        evidence: str | None,
    ) -> str:
        return "\n".join(
            [
                f"Nhân vật: {character_name}",
                f"Tác phẩm: {work_title or '(không rõ)'}",
                f"Giai đoạn: {phase_title or '(không rõ)'}",
                f"Câu hỏi: {question}",
                f"Rubric: {rubric}",
                f"Dẫn chứng gợi ý: {evidence or '(không có)'}",
                f"Câu trả lời học sinh: {answer}",
            ]
        )

    @staticmethod
    def _parse_json_object(content: str) -> dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("Expected a JSON object.")
        return parsed

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    @staticmethod
    def _confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.0
        return min(1.0, max(0.0, confidence))


_service: Optional[OpenEndedGradingService] = None


def get_open_ended_grading_service(
    knowledge_retriever: Optional["KnowledgeRetriever"] = None,
) -> OpenEndedGradingService:
    global _service
    if _service is None:
        _service = OpenEndedGradingService(knowledge_retriever=knowledge_retriever)
    return _service
