"""
Authentication domain models.

This module contains domain models for authentication operations.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class AuthResult:
    """Result of an authentication operation."""

    user_id: UUID
    email: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


@dataclass
class AuthenticatedUser:
    """Represents an authenticated user from a validated token."""

    user_id: UUID
    email: str


@dataclass
class TokenPair:
    """A pair of access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
