"""Initial Vanver schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

match_status = postgresql.ENUM(
    "SWIPED_LEFT",
    "SWIPED_RIGHT",
    "CHAT_UNLOCKED",
    "CHALLENGE_PASSED",
    name="matchstatus",
)
chat_role = postgresql.ENUM("USER", "ASSISTANT", name="chatrole")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    match_status.create(op.get_bind(), checkfirst=True)
    chat_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "characters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("author", sa.String(length=100), nullable=False),
        sa.Column("work_title", sa.String(length=200), nullable=False),
        sa.Column("short_bio", sa.Text()),
        sa.Column("avatar_url", sa.String(length=500)),
        sa.Column("difficulty_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("personality_traits", postgresql.JSON()),
        sa.Column("emotional_conflicts", sa.Text()),
        sa.Column("social_context", sa.Text()),
        sa.Column("famous_quote", sa.Text()),
        sa.Column("voice_instructions", sa.Text()),
    )
    op.create_index(op.f("ix_characters_slug"), "characters", ["slug"], unique=True)

    op.create_table(
        "matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", match_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "character_id", name="uq_user_character"),
    )

    op.create_table(
        "challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("questions", postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "challenge_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("answers", postgresql.JSON(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.Column("explanations", postgresql.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "character_id", name="uq_user_character_attempt"),
    )
    op.create_index(op.f("ix_challenge_attempts_user_id"), "challenge_attempts", ["user_id"])
    op.create_index(op.f("ix_challenge_attempts_character_id"), "challenge_attempts", ["character_id"])
    op.create_index(op.f("ix_challenge_attempts_created_at"), "challenge_attempts", ["created_at"])

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", chat_role, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_chat_messages_user_id"), "chat_messages", ["user_id"])
    op.create_index(op.f("ix_chat_messages_character_id"), "chat_messages", ["character_id"])
    op.create_index(op.f("ix_chat_messages_created_at"), "chat_messages", ["created_at"])

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chunk_id", sa.String(length=200), nullable=False),
        sa.Column("document_id", sa.String(length=200), nullable=False),
        sa.Column("character_slug", sa.String(length=100), nullable=False),
        sa.Column("character_name", sa.String(length=100), nullable=False),
        sa.Column("work_title", sa.String(length=200)),
        sa.Column("author", sa.String(length=100)),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=False),
        sa.Column("text_hash", sa.String(length=64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.Column("embedding", Vector(3072), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("chunk_id", name="uq_knowledge_chunk_id"),
    )
    op.create_index(op.f("ix_knowledge_chunks_chunk_id"), "knowledge_chunks", ["chunk_id"])
    op.create_index(op.f("ix_knowledge_chunks_document_id"), "knowledge_chunks", ["document_id"])
    op.create_index(op.f("ix_knowledge_chunks_character_slug"), "knowledge_chunks", ["character_slug"])
    op.create_index(op.f("ix_knowledge_chunks_doc_type"), "knowledge_chunks", ["doc_type"])
    op.create_index(op.f("ix_knowledge_chunks_embedding_model"), "knowledge_chunks", ["embedding_model"])


def downgrade() -> None:
    op.drop_table("knowledge_chunks")
    op.drop_table("chat_messages")
    op.drop_table("challenge_attempts")
    op.drop_table("challenges")
    op.drop_table("matches")
    op.drop_table("characters")
    op.drop_table("users")
    chat_role.drop(op.get_bind(), checkfirst=True)
    match_status.drop(op.get_bind(), checkfirst=True)
