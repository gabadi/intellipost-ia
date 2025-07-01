"""
User repository protocol for user management module.

This module defines the Protocol interface for user data persistence operations.
"""

from typing import Protocol
from uuid import UUID

from modules.user_management.domain.entities.user import User


class UserRepositoryProtocol(Protocol):
    """Protocol for user data persistence operations."""

    async def create(self, user: User) -> User:
        """Create a new user."""
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        ...

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        ...

    async def update(self, user: User) -> User:
        """Update an existing user."""
        ...

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        ...
