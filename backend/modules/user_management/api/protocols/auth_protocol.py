"""
Authentication protocol for user management module.

This module defines the protocol for current user authentication,
allowing the module to be used without depending on external API modules.
"""

from typing import Protocol

from modules.user_management.domain.entities.user import User


class CurrentUserProtocol(Protocol):
    """Protocol for getting the current authenticated user."""

    async def __call__(self) -> User:
        """Get the current authenticated user."""
        ...
