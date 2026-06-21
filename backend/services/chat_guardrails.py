"""Lightweight guardrails for character chat requests."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal


GuardrailReason = Literal["off_topic", "other_character_voice"]


@dataclass(frozen=True)
class ChatGuardrailResult:
    reason: GuardrailReason
    response: str


_OFF_TOPIC_PATTERNS = (
    re.compile(r"(?<!\w)\d+\s*(?:\+|-|\*|/|x|×|÷)\s*\d+(?!\w)"),
    re.compile(r"\b(?:cong|tru|nhan|chia)\s+\d+\b"),
    re.compile(
        r"\b(?:python|javascript|typescript|java|sql|html|css|code|coding|"
        r"lap trinh|chuong trinh|function|ham|thuat toan)\b"
    ),
    re.compile(
        r"\b(?:dao ham|tich phan|phuong trinh|hinh hoc|excel|bitcoin|"
        r"gia vang|thoi tiet|may gio|tin tuc)\b"
    ),
)

_DIALOGUE_CUES = (
    "loi thoai",
    "cau thoai",
    "noi lai loi",
    "trich loi",
    "doc lai loi",
    "quote",
)

_VOICE_SHIFT_CUES = (
    "noi thay",
    "dong vai",
    "nhap vai",
    "tra loi nhu",
    "noi nhu",
)

_OTHER_CHARACTER_ALIASES = (
    "ong giao",
    "thi no",
    "ba kien",
    "ly cuong",
    "tu lang",
    "a phu",
    "a su",
    "pa tra",
    "thong ly pa tra",
    "be thu",
    "ong sau",
    "truong sinh",
    "be dan",
    "thuy van",
    "kim trong",
    "tu hai",
    "hoan thu",
    "cai le",
    "anh dau",
)


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.lower())
    without_marks = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    without_marks = without_marks.replace("đ", "d")
    return " ".join(without_marks.split())


def evaluate_chat_guardrail(
    user_message: str,
    *,
    character_name: str,
) -> ChatGuardrailResult | None:
    normalized = normalize_text(user_message)
    selected_character = normalize_text(character_name)
    if not normalized:
        return None

    if any(pattern.search(normalized) for pattern in _OFF_TOPIC_PATTERNS):
        return ChatGuardrailResult(
            reason="off_topic",
            response=_off_topic_response(character_name),
        )

    if _asks_for_other_character_voice(normalized, selected_character):
        return ChatGuardrailResult(
            reason="other_character_voice",
            response=_other_character_voice_response(character_name),
        )

    return None


def _asks_for_other_character_voice(
    normalized_message: str,
    selected_character: str,
) -> bool:
    has_voice_shift = any(cue in normalized_message for cue in _VOICE_SHIFT_CUES)
    has_dialogue_cue = any(cue in normalized_message for cue in _DIALOGUE_CUES)
    if not has_voice_shift and not has_dialogue_cue:
        return False

    mentioned_other_character = any(
        alias in normalized_message and alias not in selected_character
        for alias in _OTHER_CHARACTER_ALIASES
    )
    if mentioned_other_character:
        return True

    return has_voice_shift and selected_character not in normalized_message


def _off_topic_response(character_name: str) -> str:
    return (
        f"Chuyện ấy không thuộc phần đời của {character_name}.\n\n"
        "Tôi không rành những phép tính hay chuyện lập trình ngoài kia. "
        "Nếu muốn nói tiếp, hãy hỏi tôi về nỗi khổ, lựa chọn, kỷ niệm "
        "hoặc những người đi qua đời tôi."
    )


def _other_character_voice_response(character_name: str) -> str:
    return (
        f"Tôi là {character_name}, nên không nói thay lời người khác được.\n\n"
        "Tôi chỉ có thể kể điều mình thấy, mình biết, hoặc điều còn đau "
        "trong lòng mình. Nếu hỏi theo góc nhìn của tôi, tôi sẽ trả lời."
    )
