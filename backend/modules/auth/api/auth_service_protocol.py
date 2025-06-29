"""
Authentication service protocol for API layer.

This module defines what the API layer needs from an authentication service.
The protocol is defined by the client (API), not the provider (auth domain).
"""

from typing import Protocol

from modules.auth.domain.models import AuthenticatedUser, AuthResult


class AuthenticationServiceProtocol(Protocol):
    """
    Authentication service protocol interface.

    Defines what the API layer needs from an authentication service.
    The concrete implementation is in the auth application layer.
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
        """
        ...

    async def validate_token(self, access_token: str) -> AuthenticatedUser:
        """
        Validate an access token and return user information.

        Args:
            access_token: JWT access token

        Returns:
            AuthenticatedUser: User information from token
        """
        ...

    async def refresh_token(self, refresh_token: str) -> str:
        """
        Create a new access token from a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            str: New access token
        """
        ...

    async def logout_user(self, refresh_token: str) -> bool:
        """
        Logout user by invalidating refresh token.

        Args:
            refresh_token: Refresh token to invalidate

        Returns:
            bool: True if logout successful, False otherwise
        """
        ...
