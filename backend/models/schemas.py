"""
Pydantic schemas for request / response validation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────


class MatchStatus(str, Enum):
    SWIPED_LEFT = "SWIPED_LEFT"
    SWIPED_RIGHT = "SWIPED_RIGHT"
    CHAT_UNLOCKED = "CHAT_UNLOCKED"
    CHALLENGE_PASSED = "CHALLENGE_PASSED"


class SwipeDirection(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


# ── User ──────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    grade_level: int = Field(..., ge=10, le=12)


class UserResponse(BaseModel):
    id: UUID
    username: str
    grade_level: int
    total_score: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Character ─────────────────────────────────────────────────────────────


class CharacterCard(BaseModel):
    """Lightweight card returned for the swipe deck."""

    id: UUID
    slug: str
    name: str
    author: str
    work_title: str
    short_bio: Optional[str] = None
    avatar_url: Optional[str] = None
    difficulty_level: int
    personality_traits: Optional[List[str]] = None
    emotional_conflicts: Optional[str] = None
    social_context: Optional[str] = None
    famous_quote: Optional[str] = None

    model_config = {"from_attributes": True}


class CharacterDetail(CharacterCard):
    """Full detail including voice instructions."""

    voice_instructions: Optional[str] = None


class MatchedCharacter(CharacterCard):
    """Character card with the current user's match state."""

    match_status: MatchStatus
    matched_at: datetime


class CharacterRelationshipResponse(BaseModel):
    id: UUID
    character_id: UUID
    related_character_id: Optional[UUID] = None
    related_name: str
    relationship_type: str
    description: str
    evidence: Optional[str] = None
    source_path: Optional[str] = None

    model_config = {"from_attributes": True}


class CharacterRelationshipsResponse(BaseModel):
    relationships: List[CharacterRelationshipResponse]


class CharacterEventResponse(BaseModel):
    id: UUID
    character_id: UUID
    sequence_number: int
    title: str
    description: str
    source_path: Optional[str] = None

    model_config = {"from_attributes": True}


class CharacterEventsResponse(BaseModel):
    events: List[CharacterEventResponse]


class RagDiagnosticsResponse(BaseModel):
    vector_extension_enabled: bool
    embedding_model: str
    embedding_dimensions: int
    rag_top_k: int
    rag_min_similarity: float
    vector_chunk_count: int
    vector_chunks_by_character: dict[str, int]
    lexical_index_path: str
    lexical_chunk_count: int
    fallback_available: bool
    last_error: Optional[str] = None


# ── Deck ──────────────────────────────────────────────────────────────────


class DeckResponse(BaseModel):
    characters: List[CharacterCard]


class MatchedCharactersResponse(BaseModel):
    characters: List[MatchedCharacter]


# ── Swipe / Match ─────────────────────────────────────────────────────────


class SwipeRequest(BaseModel):
    user_id: UUID
    character_id: UUID
    direction: SwipeDirection


class SwipeResponse(BaseModel):
    matched: bool
    points_earned: int
    match_status: Optional[MatchStatus] = None


# ── Chat ──────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    user_id: UUID
    character_id: UUID
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: UUID
    user_id: UUID
    character_id: UUID
    role: ChatRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]


# ── Challenge ─────────────────────────────────────────────────────────────


class ChallengeQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    # NOTE: correct_answer_index is intentionally omitted from response
    # to prevent cheating.  It is only used server-side for grading.
    explanation: Optional[str] = None


class ChallengeQuestionsResponse(BaseModel):
    character_id: UUID
    questions: List[ChallengeQuestion]


class ChallengeSubmission(BaseModel):
    user_id: UUID
    character_id: UUID
    answers: List[int] = Field(
        ...,
        description="List of selected option indices, one per question.",
    )


class ChallengeResult(BaseModel):
    score: int
    total: int
    passed: bool
    points_earned: int
    explanations: List[str]
    # Per-question correct answer indices, returned post-submission so the
    # FE can highlight which option was right without leaking answers in
    # the pre-submission `GET /characters/:id/challenge` response.
    correct_answers: List[int]


class OpenEndedGradeSubmission(BaseModel):
    character_slug: str = Field(..., min_length=1)
    character_name: str = Field(..., min_length=1)
    work_title: Optional[str] = None
    phase_title: Optional[str] = None
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    rubric: str = Field(..., min_length=1)
    evidence: Optional[str] = None


class OpenEndedGradeResult(BaseModel):
    score: int = Field(..., ge=0, le=1)
    passed: bool
    feedback: str
    matched_criteria: List[str] = Field(default_factory=list)
    missing_criteria: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)
    retrieval_mode: str
    sources: List[dict] = Field(default_factory=list)


class ChallengeAttemptResponse(BaseModel):
    """Persisted attempt row. Does not include `correct_answers` because
    the DB doesn't store them — they're derived from the challenge questions
    at submission time. If a caller needs them, hit `POST /challenges/submit`
    or fetch the underlying challenge separately."""

    id: UUID
    user_id: UUID
    character_id: UUID
    answers: List[int]
    score: int
    total: int
    passed: bool
    points_earned: int
    explanations: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Leaderboard ───────────────────────────────────────────────────────────


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    username: str
    total_score: int
    characters_unlocked: int

    model_config = {"from_attributes": True}


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
