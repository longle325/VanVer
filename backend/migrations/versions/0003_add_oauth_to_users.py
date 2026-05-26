"""Add OAuth identity fields to users

Revision ID: 0003_add_oauth_to_users
Revises: 0002_character_graph_data
Create Date: 2026-05-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_add_oauth_to_users"
down_revision: Union[str, None] = "0002_character_graph_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=320), nullable=True))
    op.add_column(
        "users", sa.Column("display_name", sa.String(length=120), nullable=True)
    )
    op.add_column(
        "users", sa.Column("auth_provider", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "users", sa.Column("auth_subject", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_auth_provider"), "users", ["auth_provider"], unique=False)
    op.create_unique_constraint(
        "uq_users_auth_provider_subject",
        "users",
        ["auth_provider", "auth_subject"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_users_auth_provider_subject", "users", type_="unique")
    op.drop_index(op.f("ix_users_auth_provider"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "auth_subject")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "display_name")
    op.drop_column("users", "email")
