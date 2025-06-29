"""
Authentication domain protocols.

This module contains protocol definitions for types used within the auth module,
eliminating the need for direct dependencies on other domain modules.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from .user_status import AuthUserStatus

if TYPE_CHECKING:
    from .models import AuthenticatedUser, AuthResult
    from .value_objects import CreatedAuthUser


class AuthUserProtocol(Protocol):
    """
    Protocol defining the interface that auth module needs from User entities.

    This protocol allows the auth module to work with User objects without
    directly depending on the user domain module, maintaining clean boundaries.
    """

    # Core properties needed for authentication
    id: UUID
    email: str
    password_hash: str

    # Profile properties
    first_name: str | None
    last_name: str | None
    status: AuthUserStatus

    # Timestamps
    created_at: datetime
    updated_at: datetime | None
    last_login_at: datetime | None
    email_verified_at: datetime | None

    # Computed properties
    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        ...


class PasswordServiceProtocol(Protocol):
    """Password service protocol interface."""

    def hash_password(self, password: str) -> str:
        """Hash a plain text password."""
        ...

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        ...


class TokenPairProtocol(Protocol):
    """Token pair protocol interface."""

    access_token: str
    refresh_token: str
    expires_in: int


class JWTServiceProtocol(Protocol):
    """JWT service protocol interface."""

    def create_token_pair(
        self, user_id: "UUID", email: str, is_active: bool
    ) -> TokenPairProtocol:
        """Create access and refresh token pair."""
        ...

    def validate_access_token(self, token: str) -> "AuthenticatedUser":
        """Validate access token and return user info."""
        ...

    def validate_refresh_token(self, token: str) -> "AuthenticatedUser":
        """Validate refresh token and return user info."""
        ...

    def create_access_token_from_refresh(self, refresh_token: str) -> str:
        """Create new access token from refresh token."""
        ...


# Exception protocols to eliminate dependencies on user domain exceptions
class AuthExceptionProtocol(Protocol):
    """Base auth exception protocol."""

    pass


class UserNotFoundErrorProtocol(AuthExceptionProtocol, Protocol):
    """User not found exception protocol."""

    pass


class UserAlreadyExistsErrorProtocol(AuthExceptionProtocol, Protocol):
    """User already exists exception protocol."""

    pass


class InvalidCredentialsErrorProtocol(AuthExceptionProtocol, Protocol):
    """Invalid credentials exception protocol."""

    pass


class UserNotActiveErrorProtocol(AuthExceptionProtocol, Protocol):
    """User not active exception protocol."""

    pass


class CreateUserRequestProtocol(Protocol):
    """
    Protocol defining the data needed to create a new user.

    This protocol allows auth to send user creation requests
    to the user service without tight coupling.
    """

    email: str
    password_hash: str
    first_name: str | None
    last_name: str | None
    status: "AuthUserStatus"


class UserServiceProtocol(Protocol):
    """
    Protocol defining the interface for user service operations.

    This protocol allows auth module to interact with user operations
    without depending on the user application layer implementation.
    """

    async def create_user(
        self, user_data: CreateUserRequestProtocol
    ) -> "AuthUserProtocol":
        """
        Create a new user with the provided data.

        Args:
            user_data: User creation data

        Returns:
            AuthUserProtocol: The created user entity

        Raises:
            UserAlreadyExistsErrorProtocol: If user with email already exists
            ValueError: If user data is invalid
        """
        ...

    async def get_user_by_email(self, email: str) -> "AuthUserProtocol | None":
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            AuthUserProtocol | None: User entity if found, None otherwise
        """
        ...

    async def get_user_by_id(self, user_id: UUID) -> "AuthUserProtocol | None":
        """
        Get user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            AuthUserProtocol | None: User entity if found, None otherwise
        """
        ...


class AuthenticationServiceProtocol(Protocol):
    """
    Authentication service protocol interface.

    Defines the interface for authentication services used throughout
    the auth module.
    """

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> "AuthResult":
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

    async def authenticate_user(self, email: str, password: str) -> "AuthResult":
        """
        Authenticate user with email and password.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            AuthResult: Authentication result with user and tokens
        """
        ...

    async def validate_token(self, access_token: str) -> "AuthenticatedUser":
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

    async def get_user_profile(self, access_token: str) -> "CreatedAuthUser":
        """
        Get user profile using access token.

        Args:
            access_token: JWT access token

        Returns:
            CreatedAuthUser: User profile information

        Raises:
            JWTError: If token is invalid or expired
        """
        ...
