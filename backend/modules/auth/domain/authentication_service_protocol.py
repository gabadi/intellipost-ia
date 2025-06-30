"""
Authentication service protocol.

This module defines the protocol for authentication services following duck typing.
"""

from typing import Protocol
from uuid import UUID

from .models import AuthenticatedUser, AuthResult, TokenPair


class AuthenticationService(Protocol):
    """Protocol for authentication services."""

    async def register_user(self, email: str, password: str) -> AuthResult:
        """
        Register a new user and return authentication tokens.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            AuthResult with user details and tokens

        Raises:
            ValueError: If email is invalid or already exists
            ValueError: If password doesn't meet requirements
        """
        ...

    async def authenticate_user(self, email: str, password: str) -> AuthResult:
        """
        Authenticate user credentials and return tokens.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            AuthResult with user details and tokens

        Raises:
            ValueError: If credentials are invalid
            ValueError: If account is locked due to failed attempts
        """
        ...

    async def validate_token(self, access_token: str) -> AuthenticatedUser:
        """
        Validate an access token and return user information.

        Args:
            access_token: JWT access token

        Returns:
            AuthenticatedUser information

        Raises:
            ValueError: If token is invalid or expired
        """
        ...

    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """
        Refresh authentication tokens using a refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            New TokenPair with fresh access and refresh tokens

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        ...

    async def logout_user(self, user_id: UUID) -> None:
        """
        Logout user by invalidating their refresh tokens.

        Args:
            user_id: User UUID to logout
        """
        ...
