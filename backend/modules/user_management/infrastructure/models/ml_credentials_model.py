"""
SQLAlchemy ML Credentials model for user management module.

This module contains the SQLAlchemy model for ML credentials persistence.
"""

from datetime import UTC, datetime
from uuid import UUID as UUIDType
from uuid import uuid4

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base
from modules.user_management.domain.entities.ml_credentials import MLCredentials


class MLCredentialsModel(Base):
    """SQLAlchemy model for ML credentials entity."""

    __tablename__ = "ml_credentials"

    # Core identity
    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, index=True
    )
    user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # MercadoLibre app credentials
    ml_app_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ml_secret_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)

    # OAuth tokens (encrypted)
    ml_access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    ml_refresh_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    ml_token_type: Mapped[str] = mapped_column(
        String(50), default="bearer", nullable=False
    )
    ml_expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, index=True
    )
    ml_refresh_expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, index=True
    )

    # OAuth scopes and permissions
    ml_scopes: Mapped[str] = mapped_column(
        String(255), default="offline_access read write", nullable=False
    )

    # MercadoLibre user information
    ml_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ml_nickname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ml_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Country-specific data (ENHANCED per story)
    ml_site_id: Mapped[str] = mapped_column(
        String(10), default="MLA", nullable=False, index=True
    )
    ml_auth_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Connection health and validation
    ml_is_valid: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    ml_last_validated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    ml_validation_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # PKCE temporary storage during OAuth flow (ENHANCED per story)
    pkce_code_challenge: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pkce_code_verifier: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def to_domain(self) -> MLCredentials:
        """Convert SQLAlchemy model to domain entity."""
        return MLCredentials(
            id=self.id,
            user_id=self.user_id,
            ml_app_id=self.ml_app_id,
            ml_secret_key_encrypted=self.ml_secret_key_encrypted,
            ml_access_token_encrypted=self.ml_access_token_encrypted,
            ml_refresh_token_encrypted=self.ml_refresh_token_encrypted,
            ml_token_type=self.ml_token_type,
            ml_expires_at=self.ml_expires_at,
            ml_refresh_expires_at=self.ml_refresh_expires_at,
            ml_scopes=self.ml_scopes,
            ml_user_id=self.ml_user_id,
            ml_nickname=self.ml_nickname,
            ml_email=self.ml_email,
            ml_site_id=self.ml_site_id,
            ml_auth_domain=self.ml_auth_domain,
            ml_is_valid=self.ml_is_valid,
            ml_last_validated_at=self.ml_last_validated_at,
            ml_validation_error=self.ml_validation_error,
            pkce_code_challenge=self.pkce_code_challenge,
            pkce_code_verifier=self.pkce_code_verifier,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, credentials: MLCredentials) -> "MLCredentialsModel":
        """Create SQLAlchemy model from domain entity."""
        return cls(
            id=credentials.id,
            user_id=credentials.user_id,
            ml_app_id=credentials.ml_app_id,
            ml_secret_key_encrypted=credentials.ml_secret_key_encrypted,
            ml_access_token_encrypted=credentials.ml_access_token_encrypted,
            ml_refresh_token_encrypted=credentials.ml_refresh_token_encrypted,
            ml_token_type=credentials.ml_token_type,
            ml_expires_at=credentials.ml_expires_at,
            ml_refresh_expires_at=credentials.ml_refresh_expires_at,
            ml_scopes=credentials.ml_scopes,
            ml_user_id=credentials.ml_user_id,
            ml_nickname=credentials.ml_nickname,
            ml_email=credentials.ml_email,
            ml_site_id=credentials.ml_site_id,
            ml_auth_domain=credentials.ml_auth_domain,
            ml_is_valid=credentials.ml_is_valid,
            ml_last_validated_at=credentials.ml_last_validated_at,
            ml_validation_error=credentials.ml_validation_error,
            pkce_code_challenge=credentials.pkce_code_challenge,
            pkce_code_verifier=credentials.pkce_code_verifier,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at,
        )

    def update_from_domain(self, credentials: MLCredentials) -> None:
        """Update SQLAlchemy model from domain entity."""
        self.ml_app_id = credentials.ml_app_id
        self.ml_secret_key_encrypted = credentials.ml_secret_key_encrypted
        self.ml_access_token_encrypted = credentials.ml_access_token_encrypted
        self.ml_refresh_token_encrypted = credentials.ml_refresh_token_encrypted
        self.ml_token_type = credentials.ml_token_type
        self.ml_expires_at = credentials.ml_expires_at
        self.ml_refresh_expires_at = credentials.ml_refresh_expires_at
        self.ml_scopes = credentials.ml_scopes
        self.ml_user_id = credentials.ml_user_id
        self.ml_nickname = credentials.ml_nickname
        self.ml_email = credentials.ml_email
        self.ml_site_id = credentials.ml_site_id
        self.ml_auth_domain = credentials.ml_auth_domain
        self.ml_is_valid = credentials.ml_is_valid
        self.ml_last_validated_at = credentials.ml_last_validated_at
        self.ml_validation_error = credentials.ml_validation_error
        self.pkce_code_challenge = credentials.pkce_code_challenge
        self.pkce_code_verifier = credentials.pkce_code_verifier
        self.updated_at = credentials.updated_at
