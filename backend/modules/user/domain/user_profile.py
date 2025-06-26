"""
User profile management logic.

This module contains methods for managing user profile information.
"""

from .user_core import UserCore


class UserProfile:
    """Profile management methods for user entities."""

    @staticmethod
    def get_full_name(user: UserCore) -> str:
        """Get user's full name."""
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        elif user.first_name:
            return user.first_name
        elif user.last_name:
            return user.last_name
        else:
            return user.email.split("@")[0]
