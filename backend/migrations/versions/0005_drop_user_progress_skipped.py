"""Drop redundant user_progress.skipped column

Skip state is now sourced solely from Match rows (SWIPED_LEFT). The deck is
already computed from Match rows, so the parallel ``user_progress.skipped``
array duplicated that data and was the reason the "reopen skipped cards" button
never repopulated the deck. Removing it leaves Match rows as the single source
of truth for swipe state.

Revision ID: 0005_drop_user_progress_skipped
Revises: 0004_add_user_progress
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_drop_user_progress_skipped"
down_revision: Union[str, None] = "0004_add_user_progress"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user_progress", "skipped")


def downgrade() -> None:
    op.add_column(
        "user_progress",
        sa.Column(
            "skipped",
            postgresql.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )
    op.alter_column("user_progress", "skipped", server_default=None)
