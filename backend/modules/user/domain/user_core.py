"""
User domain entity core.

This module contains the core User entity dataclass and basic properties.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from .user_status import UserStatus


@dataclass
class UserCore:
    """
    Core User domain entity representing an application user.

    This entity contains the essential data structure for user accounts.
    """

    id: UUID
    email: str
    password_hash: str
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
            self.updated_at = datetime.now(UTC)
