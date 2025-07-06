"""Seed default admin user

Revision ID: 002_seed_default_admin_user
Revises: 001_create_users
Create Date: 2025-01-06 10:00:00.000000

"""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_seed_default_admin_user"
down_revision: str | None = "001_create_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create default admin user."""
    # We'll use bcrypt to hash the password
    import bcrypt

    # Default admin credentials
    admin_email = "admin@intellipost.ai"
    admin_password = "admin123"

    # Hash the password
    password_hash = bcrypt.hashpw(
        admin_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    # Create the admin user
    admin_user = {
        "id": str(uuid4()),
        "email": admin_email,
        "password_hash": password_hash,
        "first_name": "Admin",
        "last_name": "User",
        "status": "active",
        "is_active": True,
        "is_email_verified": True,
        "failed_login_attempts": 0,
        "last_failed_login_at": None,
        "password_reset_token": None,
        "password_reset_expires_at": None,
        "email_verification_token": None,
        "ml_user_id": None,
        "ml_access_token": None,
        "ml_refresh_token": None,
        "ml_token_expires_at": None,
        "default_ml_site": "MLA",
        "auto_publish": False,
        "ai_confidence_threshold": "medium",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_login_at": None,
        "email_verified_at": datetime.now(UTC),
    }

    # Check if admin user already exists
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT id FROM users WHERE email = :email"), {"email": admin_email}
    ).fetchone()

    if result is None:
        # Insert admin user only if it doesn't exist
        connection.execute(
            sa.text("""
                INSERT INTO users (
                    id, email, password_hash, first_name, last_name, status,
                    is_active, is_email_verified, failed_login_attempts,
                    last_failed_login_at, password_reset_token, password_reset_expires_at,
                    email_verification_token, ml_user_id, ml_access_token, ml_refresh_token,
                    ml_token_expires_at, default_ml_site, auto_publish, ai_confidence_threshold,
                    created_at, updated_at, last_login_at, email_verified_at
                ) VALUES (
                    :id, :email, :password_hash, :first_name, :last_name, :status,
                    :is_active, :is_email_verified, :failed_login_attempts,
                    :last_failed_login_at, :password_reset_token, :password_reset_expires_at,
                    :email_verification_token, :ml_user_id, :ml_access_token, :ml_refresh_token,
                    :ml_token_expires_at, :default_ml_site, :auto_publish, :ai_confidence_threshold,
                    :created_at, :updated_at, :last_login_at, :email_verified_at
                )
            """),
            admin_user,
        )
        print(f"Created default admin user: {admin_email}")
    else:
        print(f"Admin user already exists: {admin_email}")


def downgrade() -> None:
    """Remove default admin user."""
    admin_email = "admin@intellipost.ai"

    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM users WHERE email = :email"), {"email": admin_email}
    )
    print(f"Removed default admin user: {admin_email}")
