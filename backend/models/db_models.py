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

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    grade_level = Column(Integer, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)
    email = Column(String(320), nullable=True, index=True)
    display_name = Column(String(120), nullable=True)
    auth_provider = Column(String(50), nullable=True, index=True)
    auth_subject = Column(String(255), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # relationships
    matches = relationship("Match", back_populates="user", lazy="selectin")
    chat_messages = relationship("ChatMessage", back_populates="user", lazy="selectin")
    challenge_attempts = relationship(
        "ChallengeAttempt",
        back_populates="user",
        lazy="selectin",
    )
    progress = relationship(
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    work_title = Column(String(200), nullable=False)
    short_bio = Column(Text)
    avatar_url = Column(String(500))
    difficulty_level = Column(Integer, default=1, nullable=False)
    personality_traits = Column(JSON)  # JSONB list of strings
    emotional_conflicts = Column(Text)
    social_context = Column(Text)
    famous_quote = Column(Text)
    voice_instructions = Column(Text)  # override prompt for chat

    # relationships
    challenges = relationship("Challenge", back_populates="character", lazy="selectin")
    matches = relationship("Match", back_populates="character", lazy="selectin")
    chat_messages = relationship(
        "ChatMessage",
        back_populates="character",
        lazy="selectin",
    )
    challenge_attempts = relationship(
        "ChallengeAttempt",
        back_populates="character",
        lazy="selectin",
    )
    relationships = relationship(
        "CharacterRelationship",
        foreign_keys="CharacterRelationship.character_id",
        back_populates="character",
        lazy="selectin",
    )
    events = relationship("CharacterEvent", back_populates="character", lazy="selectin")


# ---------------------------------------------------------------------------
# Matches  (user <-> character state)
# ---------------------------------------------------------------------------
class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(Enum(MatchStatus), default=MatchStatus.SWIPED_RIGHT, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # relationships
    user = relationship("User", back_populates="matches")
    character = relationship("Character", back_populates="matches")


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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    questions = Column(JSON, nullable=False)

    # relationships
    character = relationship("Character", back_populates="challenges")


# ---------------------------------------------------------------------------
# Challenge attempts
# ---------------------------------------------------------------------------
class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"
    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character_attempt"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answers = Column(JSON, nullable=False)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    points_earned = Column(Integer, nullable=False)
    explanations = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # relationships
    user = relationship("User", back_populates="challenge_attempts")
    character = relationship("Character", back_populates="challenge_attempts")


# ---------------------------------------------------------------------------
# User progress
# ---------------------------------------------------------------------------
class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    completed = Column(JSON, default=dict, nullable=False)
    level_results = Column(JSON, default=dict, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="progress")


# ---------------------------------------------------------------------------
# Chat messages
# ---------------------------------------------------------------------------
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(Enum(ChatRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # relationships
    user = relationship("User", back_populates="chat_messages")
    character = relationship("Character", back_populates="chat_messages")


# ---------------------------------------------------------------------------
# Knowledge chunks
# ---------------------------------------------------------------------------
class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        UniqueConstraint("chunk_id", name="uq_knowledge_chunk_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(String(200), nullable=False, index=True)
    document_id = Column(String(200), nullable=False, index=True)
    character_slug = Column(String(100), nullable=False, index=True)
    character_name = Column(String(100), nullable=False)
    work_title = Column(String(200))
    author = Column(String(100))
    doc_type = Column(String(50), nullable=False, index=True)
    source_path = Column(Text, nullable=False)
    text_hash = Column(String(64), nullable=False)
    text = Column(Text, nullable=False)
    embedding_model = Column(String(100), nullable=False, index=True)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    related_character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    related_name = Column(String(100), nullable=False)
    relationship_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text)
    source_path = Column(Text)

    character = relationship(
        "Character",
        foreign_keys=[character_id],
        back_populates="relationships",
    )
    related_character = relationship("Character", foreign_keys=[related_character_id])


class CharacterEvent(Base):
    __tablename__ = "character_events"
    __table_args__ = (
        UniqueConstraint("character_id", "sequence_number", name="uq_character_event_sequence"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    source_path = Column(Text)

    character = relationship("Character", back_populates="events")
