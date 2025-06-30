"""
SQLAlchemy models for user domain.

This module contains the database models for users and authentication.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.database import Base


class UserModel(Base):
    """SQLAlchemy model for users table."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # User profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="pending_verification", nullable=False)

    # MercadoLibre integration
    ml_user_id = Column(String(100), nullable=True)
    ml_access_token = Column(String(500), nullable=True)
    ml_refresh_token = Column(String(500), nullable=True)
    ml_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Preferences
    default_ml_site = Column(String(10), default="MLA", nullable=False)
    auto_publish = Column(Boolean, default=False, nullable=False)
    ai_confidence_threshold = Column(String(20), default="medium", nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    # Rate limiting
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_tokens = relationship(
        "RefreshTokenModel", back_populates="user", cascade="all, delete-orphan"
    )


class RefreshTokenModel(Base):
    """SQLAlchemy model for refresh_tokens table."""

    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    # Relationships
    user = relationship("UserModel", back_populates="refresh_tokens")
