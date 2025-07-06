"""
SQLAlchemy User model for user management module.

This module contains the SQLAlchemy model for User entity persistence.
"""

from datetime import UTC, datetime
from uuid import UUID as UUIDType
from uuid import uuid4

from sqlalchemy import TIMESTAMP, Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

from modules.user_management.domain.entities.user import User, UserStatus

Base = declarative_base()


class UserModel(Base):
    """SQLAlchemy model for User entity."""

    __tablename__ = "users"

    # Core identity
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    # User profile
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=UserStatus.PENDING_VERIFICATION.value, nullable=False
    )

    # Authentication fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_failed_login_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    password_reset_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    email_verification_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    # MercadoLibre integration
    ml_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ml_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    ml_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    ml_token_expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # Preferences
    default_ml_site: Mapped[str] = mapped_column(
        String(10), default="MLA", nullable=False
    )
    auto_publish: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_confidence_threshold: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    def to_domain(self) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=self.id,
            email=self.email,
            password_hash=self.password_hash,
            created_at=self.created_at,
            first_name=self.first_name,
            last_name=self.last_name,
            status=UserStatus(self.status),
            is_active=self.is_active,
            is_email_verified=self.is_email_verified,
            failed_login_attempts=self.failed_login_attempts,
            last_failed_login_at=self.last_failed_login_at,
            password_reset_token=self.password_reset_token,
            password_reset_expires_at=self.password_reset_expires_at,
            email_verification_token=self.email_verification_token,
            ml_user_id=self.ml_user_id,
            ml_access_token=self.ml_access_token,
            ml_refresh_token=self.ml_refresh_token,
            ml_token_expires_at=self.ml_token_expires_at,
            default_ml_site=self.default_ml_site,
            auto_publish=self.auto_publish,
            ai_confidence_threshold=self.ai_confidence_threshold,
            updated_at=self.updated_at,
            last_login_at=self.last_login_at,
            email_verified_at=self.email_verified_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        """Create SQLAlchemy model from domain entity."""
        return cls(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status.value,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            failed_login_attempts=user.failed_login_attempts,
            last_failed_login_at=user.last_failed_login_at,
            password_reset_token=user.password_reset_token,
            password_reset_expires_at=user.password_reset_expires_at,
            email_verification_token=user.email_verification_token,
            ml_user_id=user.ml_user_id,
            ml_access_token=user.ml_access_token,
            ml_refresh_token=user.ml_refresh_token,
            ml_token_expires_at=user.ml_token_expires_at,
            default_ml_site=user.default_ml_site,
            auto_publish=user.auto_publish,
            ai_confidence_threshold=user.ai_confidence_threshold,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            email_verified_at=user.email_verified_at,
        )

    def update_from_domain(self, user: User) -> None:
        """Update SQLAlchemy model from domain entity."""
        self.email = user.email
        self.password_hash = user.password_hash
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.status = user.status.value
        self.is_active = user.is_active
        self.is_email_verified = user.is_email_verified
        self.failed_login_attempts = user.failed_login_attempts
        self.last_failed_login_at = user.last_failed_login_at
        self.password_reset_token = user.password_reset_token
        self.password_reset_expires_at = user.password_reset_expires_at
        self.email_verification_token = user.email_verification_token
        self.ml_user_id = user.ml_user_id
        self.ml_access_token = user.ml_access_token
        self.ml_refresh_token = user.ml_refresh_token
        self.ml_token_expires_at = user.ml_token_expires_at
        self.default_ml_site = user.default_ml_site
        self.auto_publish = user.auto_publish
        self.ai_confidence_threshold = user.ai_confidence_threshold
        self.updated_at = user.updated_at
        self.last_login_at = user.last_login_at
        self.email_verified_at = user.email_verified_at
