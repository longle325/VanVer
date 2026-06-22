"""Lightweight guardrails for character chat requests."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal, Optional


GuardrailReason = Literal["off_topic", "other_character_voice"]


@dataclass(frozen=True)
class ChatGuardrailResult:
    reason: GuardrailReason
    response: str


_OFF_TOPIC_PATTERNS = (
    re.compile(r"(?<!\w)\d+\s*(?:\+|-|\*|/|x|×|÷)\s*\d+(?!\w)"),
    re.compile(r"\b(?:cong|tru|nhan|chia)\s+\d+\b"),
    re.compile(r"\b(?:truyen cuoi|chuyen cuoi|cau chuyen cuoi|joke|meme)\b"),
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

_GENERAL_LITERARY_TERMS = (
    "tac gia",
    "tac pham",
    "truyen nay",
    "truyen ngan",
    "tieu thuyet",
    "van hoc",
    "nhan vat",
    "phan tich",
    "giai thich",
    "dan y",
    "soan bai",
    "noi dung",
    "nghe thuat",
    "chu de",
    "tu tuong",
    "y nghia",
    "bieu tuong",
    "hinh anh",
    "chi tiet",
    "doan trich",
    "cau chuyen nay",
    "bi kich",
    "xung dot",
    "hoan canh",
    "so phan",
    "tam trang",
    "tam ly",
    "pham chat",
    "tinh cach",
    "loi thoai",
    "cau thoai",
    "ket thuc",
    "boi canh",
    "ngoi ke",
    "gia tri hien thuc",
    "gia tri nhan dao",
)

_ROLEPLAY_ADDRESS_CUES = (
    "ong",
    "ba",
    "co",
    "chu",
    "chi",
    "anh",
    "em",
    "may",
    "tao",
    "toi",
    "minh",
)

_CHARACTER_LIFE_TERMS = (
    "cuoc doi",
    "doi ong",
    "doi ba",
    "doi co",
    "doi toi",
    "doi minh",
    "doi anh",
    "doi chi",
    "doi may",
    "phan doi",
    "noi kho",
    "kho",
    "ngheo",
    "co don",
    "buon",
    "vui",
    "dau",
    "dau kho",
    "day dut",
    "an han",
    "hoi han",
    "nho",
    "mong",
    "uoc mo",
    "hy vong",
    "so",
    "so hai",
    "thuong",
    "ghet",
    "yeu",
    "cam thay",
    "tam su",
    "long",
    "ky uc",
    "ky niem",
    "qua khu",
    "tuoi tho",
    "gia dinh",
    "cha",
    "me",
    "con",
    "nguoi than",
    "vo",
    "chong",
    "song",
    "chet",
    "lua chon",
    "uoc",
)

_CHARACTER_CONTEXT_TERMS: dict[str, tuple[str, ...]] = {
    "lao_hac": (
        "lao hac",
        "nam cao",
        "cau vang",
        "ong giao",
        "ban cho",
        "manh vuon",
        "con trai",
        "ba cho",
        "lang que",
        "nguoi nong dan",
    ),
    "chi_pheo": (
        "chi pheo",
        "nam cao",
        "thi no",
        "ba kien",
        "bat chao hanh",
        "lo gach",
        "lang vu dai",
        "luong thien",
        "con quy du",
    ),
    "mi": (
        "mi",
        "to hoai",
        "vo chong a phu",
        "a phu",
        "a su",
        "pa tra",
        "hong ngai",
        "tieng sao",
        "la ngon",
        "con dau gat no",
    ),
    "xuan_toc_do": (
        "xuan toc do",
        "vu trong phung",
        "so do",
        "au hoa",
        "danh vong",
        "dia vi",
        "tien than",
        "leo len",
        "cu co hong",
        "ba pho doan",
        "tuyet",
    ),
    "luc_van_tien": (
        "luc van tien",
        "nguyen dinh chieu",
        "kieu nguyet nga",
        "van tien",
        "nguyet nga",
        "trinh ham",
        "luc van tien cuu kieu nguyet nga",
    ),
    "thuy_kieu": (
        "thuy kieu",
        "truyen kieu",
        "nguyen du",
        "kim trong",
        "thuy van",
        "tu hai",
        "hoan thu",
        "trao duyen",
        "lau ngung bich",
    ),
    "chi_dau": (
        "chi dau",
        "ngo tat to",
        "tat den",
        "anh dau",
        "cai le",
        "suu thue",
        "tuc nuoc vo bo",
        "noi chao",
    ),
    "ong_sau": (
        "ong sau",
        "nguyen quang sang",
        "chiec luoc nga",
        "be thu",
        "vet seo",
        "tieng goi ba",
        "chien tranh",
    ),
    "ong_hai": (
        "ong hai",
        "kim lan",
        "lang",
        "cho dau",
        "lang cho dau",
        "viet gian",
        "cu ho",
        "tan cu",
    ),
    "vu_nuong": (
        "vu nuong",
        "nguyen du",
        "chuyen nguoi con gai nam xuong",
        "nam xuong",
        "truong sinh",
        "be dan",
        "chiec bong",
        "hoang giang",
    ),
}

_QUESTION_OR_REQUEST_PATTERNS = (
    re.compile(r"\?"),
    re.compile(
        r"\b(?:ai|gi|sao|tai sao|vi sao|the nao|nhu the nao|khi nao|"
        r"o dau|may|bao nhieu|co phai|hay khong)\b"
    ),
    re.compile(
        r"\b(?:hay|giup|ke|noi|tra loi|tu van|goi y|viet|lam|cho toi|"
        r"cho minh|chi toi|day toi|nhac toi)\b"
    ),
)

_CONTINUATION_CUES = (
    "con sau do",
    "sau do thi sao",
    "roi sao",
    "the con",
    "vay thi sao",
    "noi tiep",
    "ke tiep",
    "chi tiet hon",
    "ro hon",
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
    character_slug: Optional[str] = None,
    has_chat_history: bool = False,
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

    if _is_unrelated_question_or_request(
        normalized,
        selected_character=selected_character,
        character_slug=character_slug,
        has_chat_history=has_chat_history,
    ):
        return ChatGuardrailResult(
            reason="off_topic",
            response=_off_topic_response(character_name),
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


def _is_unrelated_question_or_request(
    normalized_message: str,
    *,
    selected_character: str,
    character_slug: Optional[str],
    has_chat_history: bool,
) -> bool:
    if not _looks_like_question_or_request(normalized_message):
        return False

    if has_chat_history and any(
        cue in normalized_message for cue in _CONTINUATION_CUES
    ):
        return False

    return not _has_literary_relevance(
        normalized_message,
        selected_character=selected_character,
        character_slug=character_slug,
    )


def _looks_like_question_or_request(normalized_message: str) -> bool:
    return any(
        pattern.search(normalized_message)
        for pattern in _QUESTION_OR_REQUEST_PATTERNS
    )


def _has_literary_relevance(
    normalized_message: str,
    *,
    selected_character: str,
    character_slug: Optional[str],
) -> bool:
    terms = [selected_character, *_GENERAL_LITERARY_TERMS]
    if character_slug:
        terms.extend(_CHARACTER_CONTEXT_TERMS.get(character_slug, ()))
    return any(
        _contains_term(normalized_message, term) for term in terms
    ) or _is_in_character_life_prompt(normalized_message)


def _is_in_character_life_prompt(normalized_message: str) -> bool:
    has_address = any(
        _contains_term(normalized_message, term)
        for term in _ROLEPLAY_ADDRESS_CUES
    )
    if not has_address:
        return False
    return any(
        _contains_term(normalized_message, term)
        for term in _CHARACTER_LIFE_TERMS
    )


def _contains_term(normalized_message: str, term: str) -> bool:
    if not term:
        return False
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized_message) is not None


def _off_topic_response(character_name: str) -> str:
    return (
        "Câu ấy không liên quan đến tác giả, tác phẩm hay phần đời "
        f"của {character_name}.\n\n"
        "Nếu muốn nói tiếp, hãy hỏi tôi về nhân vật, chi tiết, chủ đề, "
        "mâu thuẫn hoặc những lựa chọn trong câu chuyện."
    )


def _other_character_voice_response(character_name: str) -> str:
    return (
        f"Tôi là {character_name}, nên không nói thay lời người khác được.\n\n"
        "Tôi chỉ có thể kể điều mình thấy, mình biết, hoặc điều còn đau "
        "trong lòng mình. Nếu hỏi theo góc nhìn của tôi, tôi sẽ trả lời."
    )
