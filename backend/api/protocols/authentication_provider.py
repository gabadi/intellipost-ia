"""
Authentication provider protocol for API layer.

This protocol defines what the API needs for authentication functionality.
Modules implement this protocol to provide authentication services to the API.
"""

from typing import Protocol
from uuid import UUID

from pydantic import BaseModel


class AuthenticationCredentials(BaseModel):
    """Credentials for authentication."""

    email: str
    password: str


class UserRegistrationData(BaseModel):
    """User registration data."""

    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class AuthenticatedUser(BaseModel):
    """Authenticated user data for API responses."""

    id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: str  # ISO format
    last_login_at: str | None  # ISO format


class TokenPair(BaseModel):
    """JWT token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticationResult(BaseModel):
    """Result of authentication operations."""

    user: AuthenticatedUser
    tokens: TokenPair


class AuthenticationProviderProtocol(Protocol):
    """
    Protocol defining authentication capabilities that the API requires.

    This protocol is owned by the API layer and defines what authentication
    functionality the API needs from modules. Modules implement this protocol
    to provide authentication services.
    """

    async def authenticate_user(
        self, credentials: AuthenticationCredentials
    ) -> AuthenticationResult | None:
        """
        Authenticate a user with email and password.

        Args:
            credentials: User credentials

        Returns:
            AuthenticationResult if successful, None if authentication fails
        """
        ...

    async def register_user(
        self, registration_data: UserRegistrationData
    ) -> AuthenticationResult:
        """
        Register a new user.

        Args:
            registration_data: User registration information

        Returns:
            AuthenticationResult with user and tokens

        Raises:
            UserAlreadyExistsError: If user with email already exists
            WeakPasswordError: If password doesn't meet requirements
        """
        ...

    async def refresh_tokens(self, refresh_token: str) -> AuthenticationResult | None:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            AuthenticationResult with new tokens, None if token is invalid
        """
        ...

    async def logout_user(self, access_token: str) -> bool:
        """
        Logout user and invalidate tokens.

        Args:
            access_token: User's access token

        Returns:
            True if logout successful, False otherwise
        """
        ...

    async def get_current_user(self, access_token: str) -> AuthenticatedUser | None:
        """
        Get current user from access token.

        Args:
            access_token: Valid access token

        Returns:
            AuthenticatedUser if token is valid, None otherwise
        """
        ...
