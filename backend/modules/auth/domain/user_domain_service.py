"""
User domain service protocol for authentication module.

This module defines abstract base class for user authentication domain services.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from modules.user.domain.user import User


class UserDomainService(ABC):
    """Abstract base class for user domain services."""

    @abstractmethod
    async def register_user(self, email: str, password: str) -> "User":
        """Register a new user."""
        ...

    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> "User | None":
        """Authenticate user credentials."""
        ...

    @abstractmethod
    async def verify_email(self, user_id: UUID, verification_token: str) -> bool:
        """Verify user's email address."""
        ...
