"""
User authentication and verification logic.

This module contains methods for managing user authentication state.
"""

from datetime import datetime

from .user_core import UserCore
from .user_status import UserStatus


class UserAuth:
    """Authentication and verification methods for user entities."""

    @staticmethod
    def is_active(user: UserCore) -> bool:
        """Check if user account is active."""
        return user.status == UserStatus.ACTIVE

    @staticmethod
    def is_email_verified(user: UserCore) -> bool:
        """Check if user's email is verified."""
        return user.email_verified_at is not None

    @staticmethod
    def verify_email(user: UserCore) -> None:
        """Mark user's email as verified."""
        user.email_verified_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()

    @staticmethod
    def record_login(user: UserCore) -> None:
        """Record user login timestamp."""
        user.last_login_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()

    @staticmethod
    def activate(user: UserCore) -> None:
        """Activate user account."""
        user.status = UserStatus.ACTIVE
        user.updated_at = datetime.utcnow()

    @staticmethod
    def deactivate(user: UserCore) -> None:
        """Deactivate user account."""
        user.status = UserStatus.INACTIVE
        user.updated_at = datetime.utcnow()

    @staticmethod
    def suspend(user: UserCore) -> None:
        """Suspend user account."""
        user.status = UserStatus.SUSPENDED
        user.updated_at = datetime.utcnow()
