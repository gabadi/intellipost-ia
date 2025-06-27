"""
Authentication service protocol and data models.

This module defines the authentication service protocol following
hexagonal architecture principles and related data models.
"""

from dataclasses import dataclass
from typing import Protocol
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


class AuthenticationService(Protocol):
    """
    Authentication service protocol interface.

    This protocol defines the contract for user authentication operations
    following hexagonal architecture principles.
    """

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> AuthResult:
        """
        Register a new user account.

        Args:
            email: User's email address
            password: Plain text password
            first_name: User's first name (optional)
            last_name: User's last name (optional)

        Returns:
            AuthResult: Registration result with user and tokens

        Raises:
            ValueError: If email or password is invalid
        """
        ...

    async def authenticate_user(self, email: str, password: str) -> AuthResult:
        """
        Authenticate user with email and password.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            AuthResult: Authentication result with user and tokens

        Raises:
            ValueError: If email or password is invalid
        """
        ...

    async def validate_token(self, access_token: str) -> AuthenticatedUser:
        """
        Validate an access token and return user information.

        Args:
            access_token: JWT access token

        Returns:
            AuthenticatedUser: User information from token

        Raises:
            JWTError: If token is invalid or expired
        """
        ...

    async def refresh_token(self, refresh_token: str) -> str:
        """
        Create a new access token from a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            str: New access token

        Raises:
            JWTError: If refresh token is invalid or expired
        """
        ...

    async def logout_user(self, refresh_token: str) -> bool:
        """
        Logout user by invalidating refresh token.

        Args:
            refresh_token: Refresh token to invalidate

        Returns:
            bool: True if logout successful, False otherwise

        Note:
            In this MVP implementation, we don't maintain a token blacklist,
            so this method validates the token but doesn't actually invalidate it.
            For production, consider implementing token blacklisting.
        """
        ...
