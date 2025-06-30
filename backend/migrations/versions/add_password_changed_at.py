"""add password_changed_at column

Revision ID: add_password_changed_at
Revises: 8cb75af5b3b0
Create Date: 2025-06-30 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_password_changed_at"
down_revision: str = "8cb75af5b3b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add password_changed_at column to users table."""
    op.add_column(
        "users",
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Remove password_changed_at column from users table."""
    op.drop_column("users", "password_changed_at")
