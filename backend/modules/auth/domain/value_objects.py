"""
Authentication domain value objects.

This module contains value objects used by the authentication system
to return concrete types instead of protocols, following Go principles.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreatedAuthUser:
    """
    Value object representing a user after successful registration/authentication.

    This concrete type is returned by auth operations instead of protocols,
    containing only the user information needed by the auth context.
    """

    user_id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: datetime

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
            return "Unknown User"


@dataclass(frozen=True)
class AuthTokens:
    """
    Value object representing authentication tokens.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds


@dataclass
class CreateUserRequest:
    """
    Value object for user creation requests from auth module.

    This implements the CreateUserProtocol for communication with user service.
    """

    email: str
    password_hash: str
    first_name: str | None = None
    last_name: str | None = None

    @property
    def status(self):
        """Return auth-specific status."""
        from .user_status import AuthUserStatus

        return AuthUserStatus.ACTIVE  # Auto-activate for MVP
