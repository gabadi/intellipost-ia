"""
User data persistence protocol for hexagonal architecture.

This module defines Protocol interface for user data persistence operations,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from typing import Protocol
from uuid import UUID

from .user import User


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
