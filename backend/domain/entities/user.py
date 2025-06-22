"""
User domain entity.

This module contains the User entity representing application users
with MercadoLibre integration capabilities.
"""

from dataclasses import dataclass
from datetime import datetime
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
    User domain entity representing an application user.

    This entity encapsulates user account information and MercadoLibre
    integration credentials and preferences.
    """

    id: UUID
    email: str
    created_at: datetime

    # User profile
    first_name: str | None = None
    last_name: str | None = None
    status: UserStatus = UserStatus.PENDING_VERIFICATION

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
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
    email_verified_at: datetime | None = None

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

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
            return self.email.split("@")[0]

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE

    @property
    def is_ml_connected(self) -> bool:
        """Check if user has valid MercadoLibre connection."""
        return (
            self.ml_user_id is not None
            and self.ml_access_token is not None
            and self.ml_token_expires_at is not None
            and self.ml_token_expires_at > datetime.utcnow()
        )

    @property
    def is_email_verified(self) -> bool:
        """Check if user's email is verified."""
        return self.email_verified_at is not None

    def activate(self) -> None:
        """Activate user account."""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate user account."""
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def suspend(self) -> None:
        """Suspend user account."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def verify_email(self) -> None:
        """Mark user's email as verified."""
        self.email_verified_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_ml_tokens(
        self, access_token: str, refresh_token: str, expires_at: datetime
    ) -> None:
        """Update MercadoLibre authentication tokens."""
        self.ml_access_token = access_token
        self.ml_refresh_token = refresh_token
        self.ml_token_expires_at = expires_at
        self.updated_at = datetime.utcnow()

    def record_login(self) -> None:
        """Record user login timestamp."""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
