"""
SQLAlchemy ORM models for Vanver.

Tables:
  users       - student accounts and scores
  characters  - literary character profiles
  matches     - user <-> character swipe state
  challenges  - per-character quiz questions (JSONB)
  challenge_attempts - one graded submission per user/character
  user_progress - frontend progress state synced per user
  knowledge_chunks - embedded RAG chunks from knowledge_base/index/chunks.jsonl
  character_relationships - graph-like relationship facts
  character_events - ordered character timeline events
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from core.config import settings
from core.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class MatchStatus(str, enum.Enum):
    SWIPED_LEFT = "SWIPED_LEFT"
    SWIPED_RIGHT = "SWIPED_RIGHT"
    CHAT_UNLOCKED = "CHAT_UNLOCKED"
    CHALLENGE_PASSED = "CHALLENGE_PASSED"


class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "auth_provider",
            "auth_subject",
            name="uq_users_auth_provider_subject",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False)
    total_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    auth_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    auth_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # relationships
    matches: Mapped[list["Match"]] = relationship(
        "Match", back_populates="user", lazy="selectin"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="user", lazy="selectin"
    )
    challenge_attempts: Mapped[list["ChallengeAttempt"]] = relationship(
        "ChallengeAttempt",
        back_populates="user",
        lazy="selectin",
    )
    progress: Mapped["UserProgress | None"] = relationship(
        "UserProgress",
        back_populates="user",
        lazy="selectin",
        uselist=False,
    )


# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------
class Character(Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    work_title: Mapped[str] = mapped_column(String(200), nullable=False)
    short_bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    personality_traits: Mapped[list[str] | None] = mapped_column(
        JSON
    )  # JSONB list of strings
    emotional_conflicts: Mapped[str | None] = mapped_column(Text)
    social_context: Mapped[str | None] = mapped_column(Text)
    famous_quote: Mapped[str | None] = mapped_column(Text)
    voice_instructions: Mapped[str | None] = mapped_column(
        Text
    )  # override prompt for chat

    # relationships
    challenges: Mapped[list["Challenge"]] = relationship(
        "Challenge", back_populates="character", lazy="selectin"
    )
    matches: Mapped[list["Match"]] = relationship(
        "Match", back_populates="character", lazy="selectin"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="character",
        lazy="selectin",
    )
    challenge_attempts: Mapped[list["ChallengeAttempt"]] = relationship(
        "ChallengeAttempt",
        back_populates="character",
        lazy="selectin",
    )
    relationships: Mapped[list["CharacterRelationship"]] = relationship(
        "CharacterRelationship",
        foreign_keys="CharacterRelationship.character_id",
        back_populates="character",
        lazy="selectin",
    )
    events: Mapped[list["CharacterEvent"]] = relationship(
        "CharacterEvent", back_populates="character", lazy="selectin"
    )


# ---------------------------------------------------------------------------
# Matches  (user <-> character state)
# ---------------------------------------------------------------------------
class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus), default=MatchStatus.SWIPED_RIGHT, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="matches")
    character: Mapped["Character"] = relationship("Character", back_populates="matches")


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------
class Challenge(Base):
    """
    Stores per-character challenge questions as a JSONB column.

    Expected questions JSON shape:
    [
      {
        "id": 1,
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "correct_answer_index": 2,
        "explanation": "..."
      },
      ...
    ]
    """

    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)

    # relationships
    character: Mapped["Character"] = relationship(
        "Character", back_populates="challenges"
    )


# ---------------------------------------------------------------------------
# Challenge attempts
# ---------------------------------------------------------------------------
class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"
    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character_attempt"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answers: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    explanations: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="challenge_attempts")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="challenge_attempts"
    )


# ---------------------------------------------------------------------------
# User progress
# ---------------------------------------------------------------------------
class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    completed: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    level_results: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="progress")


# ---------------------------------------------------------------------------
# Chat messages
# ---------------------------------------------------------------------------
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ChatRole] = mapped_column(Enum(ChatRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_messages")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="chat_messages"
    )


# ---------------------------------------------------------------------------
# Knowledge chunks
# ---------------------------------------------------------------------------
class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        UniqueConstraint("chunk_id", name="uq_knowledge_chunk_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chunk_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    character_slug: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    character_name: Mapped[str] = mapped_column(String(100), nullable=False)
    work_title: Mapped[str | None] = mapped_column(String(200))
    author: Mapped[str | None] = mapped_column(String(100))
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_model: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSIONS), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Character graph data
# ---------------------------------------------------------------------------
class CharacterRelationship(Base):
    __tablename__ = "character_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    related_character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    related_name: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text)
    source_path: Mapped[str | None] = mapped_column(Text)

    character: Mapped["Character"] = relationship(
        "Character",
        foreign_keys=[character_id],
        back_populates="relationships",
    )
    related_character: Mapped["Character | None"] = relationship(
        "Character", foreign_keys=[related_character_id]
    )


class CharacterEvent(Base):
    __tablename__ = "character_events"
    __table_args__ = (
        UniqueConstraint(
            "character_id", "sequence_number", name="uq_character_event_sequence"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_path: Mapped[str | None] = mapped_column(Text)

    character: Mapped["Character"] = relationship("Character", back_populates="events")
