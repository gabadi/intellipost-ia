"""
Authentication domain models.

This module contains the data models used by the authentication system.
"""

from dataclasses import dataclass
from uuid import UUID

from modules.user.domain.user import User


@dataclass
class AuthResult:
    """Result of authentication operations."""

    success: bool
    user: User | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None  # seconds
    error_message: str | None = None

    @classmethod
    def success_result(
        cls,
        user: User,
        access_token: str,
        refresh_token: str,
        expires_in: int,
    ) -> "AuthResult":
        """Create a successful authentication result."""
        return cls(
            success=True,
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    @classmethod
    def failure_result(cls, error_message: str) -> "AuthResult":
        """Create a failed authentication result."""
        return cls(
            success=False,
            error_message=error_message,
        )


@dataclass
class UserCreate:
    """Data for creating a new user."""

    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


@dataclass
class AuthenticatedUser:
    """Authenticated user information from token."""

    user_id: UUID
    email: str
    is_active: bool
    exp: int  # Token expiration timestamp
