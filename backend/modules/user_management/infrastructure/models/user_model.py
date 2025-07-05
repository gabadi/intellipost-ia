"""
SQLAlchemy user model for user management module.

This module contains the SQLAlchemy ORM model for user data persistence.
"""

from datetime import UTC, datetime
from uuid import UUID as UUIDType
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class UserModel(Base):
    """SQLAlchemy model for User entity."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )

    # Core authentication fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # User profile fields
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Account status fields
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_verification"
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Authentication tracking
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    last_failed_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Email verification
    email_verification_token: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # Password reset
    password_reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # MercadoLibre integration
    ml_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ml_access_token: Mapped[str | None] = mapped_column(
        Text,  # Use Text for longer tokens
        nullable=True,
    )
    ml_refresh_token: Mapped[str | None] = mapped_column(
        Text,  # Use Text for longer tokens
        nullable=True,
    )
    ml_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # User preferences
    default_ml_site: Mapped[str] = mapped_column(
        String(10), nullable=False, default="MLA"
    )
    auto_publish: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_confidence_threshold: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class RefreshTokenModel(Base):
    """SQLAlchemy model for refresh tokens."""

    __tablename__ = "refresh_tokens"

    # Primary key
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )

    # Foreign key to user
    user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Token data
    token_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )

    # Expiration
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
