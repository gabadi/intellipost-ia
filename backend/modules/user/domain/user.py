"""
User domain entity.

This module contains the User entity representing application users
with MercadoLibre integration capabilities.
"""

from datetime import datetime

from .user_auth import UserAuth
from .user_core import UserCore
from .user_ml_integration import UserMLIntegration
from .user_profile import UserProfile


class User(UserCore):
    """
    User domain entity representing an application user.

    This entity encapsulates user account information and MercadoLibre
    integration credentials and preferences.

    Uses composition pattern to separate concerns:
    - UserCore: Data structure and basic properties
    - UserProfile: Profile management logic
    - UserAuth: Authentication and verification logic
    - UserMLIntegration: MercadoLibre-specific logic
    """

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return UserProfile.get_full_name(self)

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return UserAuth.is_active(self)

    @property
    def is_ml_connected(self) -> bool:
        """Check if user has valid MercadoLibre connection."""
        return UserMLIntegration.is_ml_connected(self)

    @property
    def is_email_verified(self) -> bool:
        """Check if user's email is verified."""
        return UserAuth.is_email_verified(self)

    def activate(self) -> None:
        """Activate user account."""
        UserAuth.activate(self)

    def deactivate(self) -> None:
        """Deactivate user account."""
        UserAuth.deactivate(self)

    def suspend(self) -> None:
        """Suspend user account."""
        UserAuth.suspend(self)

    def verify_email(self) -> None:
        """Mark user's email as verified."""
        UserAuth.verify_email(self)

    def update_ml_tokens(
        self, access_token: str, refresh_token: str, expires_at: datetime
    ) -> None:
        """Update MercadoLibre authentication tokens."""
        UserMLIntegration.update_ml_tokens(
            self, access_token, refresh_token, expires_at
        )

    def record_login(self) -> None:
        """Record user login timestamp."""
        UserAuth.record_login(self)
