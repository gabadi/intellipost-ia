"""
Unified User domain entity for user management module.

This module contains the unified User entity combining user account,
authentication, and MercadoLibre integration functionality.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID


class UserStatus(Enum):
    """User account status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class User:
    """
    Unified User domain entity representing an application user with authentication.

    This entity combines user account information, authentication data,
    and MercadoLibre integration credentials in a single cohesive entity
    following the unified user_management bounded context.
    """

    # Core identity
    id: UUID
    email: str
    password_hash: str
    created_at: datetime

    # User profile
    first_name: str | None = None
    last_name: str | None = None
    status: UserStatus = UserStatus.PENDING_VERIFICATION

    # Authentication fields
    is_active: bool = True
    is_email_verified: bool = False
    failed_login_attempts: int = 0
    last_failed_login_at: datetime | None = None
    password_reset_token: str | None = None
    password_reset_expires_at: datetime | None = None
    email_verification_token: str | None = None

    # MercadoLibre integration
    ml_user_id: str | None = None
    ml_access_token: str | None = None
    ml_refresh_token: str | None = None
    ml_token_expires_at: datetime | None = None

    # Preferences
    default_ml_site: str = "MLA"  # Argentina by default
    auto_publish: bool = False
    ai_confidence_threshold: str = "medium"

    # Timestamps
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login_at: datetime | None = None
    email_verified_at: datetime | None = None

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        if self.updated_at is None:
            self.updated_at = datetime.now(UTC)

    # User Profile Methods
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split("@")[0]  # Fallback to email username

    # Authentication Methods
    def activate(self) -> None:
        """Activate user account."""
        self.status = UserStatus.ACTIVE
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Deactivate user account."""
        self.status = UserStatus.INACTIVE
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def suspend(self) -> None:
        """Suspend user account."""
        self.status = UserStatus.SUSPENDED
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def verify_email(self) -> None:
        """Mark user's email as verified."""
        self.is_email_verified = True
        self.email_verified_at = datetime.now(UTC)
        self.email_verification_token = None
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now(UTC)

    def record_login(self) -> None:
        """Record successful user login."""
        self.last_login_at = datetime.now(UTC)
        self.failed_login_attempts = 0
        self.last_failed_login_at = None
        self.updated_at = datetime.now(UTC)

    def record_failed_login(self) -> None:
        """Record failed login attempt."""
        self.failed_login_attempts += 1
        self.last_failed_login_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def is_account_locked(self, max_attempts: int = 5) -> bool:
        """Check if account is locked due to failed login attempts."""
        return self.failed_login_attempts >= max_attempts

    def reset_failed_logins(self) -> None:
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
        self.last_failed_login_at = None
        self.updated_at = datetime.now(UTC)

    # MercadoLibre Integration Methods
    @property
    def is_ml_connected(self) -> bool:
        """Check if user has valid MercadoLibre connection."""
        return (
            self.ml_user_id is not None
            and self.ml_access_token is not None
            and self.ml_token_expires_at is not None
            and self.ml_token_expires_at > datetime.now(UTC)
        )

    def update_ml_tokens(
        self, access_token: str, refresh_token: str, expires_at: datetime
    ) -> None:
        """Update MercadoLibre authentication tokens."""
        self.ml_access_token = access_token
        self.ml_refresh_token = refresh_token
        self.ml_token_expires_at = expires_at
        self.updated_at = datetime.now(UTC)

    def disconnect_ml(self) -> None:
        """Disconnect MercadoLibre integration."""
        self.ml_user_id = None
        self.ml_access_token = None
        self.ml_refresh_token = None
        self.ml_token_expires_at = None
        self.updated_at = datetime.now(UTC)

    def update_profile(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        auto_publish: bool | None = None,
        ai_confidence_threshold: str | None = None,
        default_ml_site: str | None = None,
    ) -> None:
        """Update user profile information."""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if auto_publish is not None:
            self.auto_publish = auto_publish
        if ai_confidence_threshold is not None:
            self.ai_confidence_threshold = ai_confidence_threshold
        if default_ml_site is not None:
            self.default_ml_site = default_ml_site
        self.updated_at = datetime.now(UTC)
