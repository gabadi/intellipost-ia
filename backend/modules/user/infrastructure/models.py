"""
User SQLAlchemy models.

This module contains the SQLAlchemy model definitions for user data persistence.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class UserModel(Base):
    """
    SQLAlchemy model for user data.

    Maps to the users table in the database following the domain entity structure.
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile fields
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_verification"
    )

    # MercadoLibre integration fields
    ml_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ml_access_token: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ml_refresh_token: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ml_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Preferences
    default_ml_site: Mapped[str] = mapped_column(
        String(10), nullable=False, default="MLA"
    )
    auto_publish: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_confidence_threshold: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        """String representation of the user model."""
        return f"<UserModel(id={self.id}, email={self.email}, status={self.status})>"
