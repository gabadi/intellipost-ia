"""
JWT service implementation for user management module.

This module provides JWT token creation and verification using python-jose.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from infrastructure.config.settings import settings


class JWTService:
    """JWT service implementation using python-jose."""

    def __init__(self) -> None:
        """Initialize JWT service with configuration from settings."""
        self._secret_key = settings.user_jwt_secret_key
        self._algorithm = "HS256"  # HS256 as specified in story requirements
        self._access_token_expire_minutes = settings.user_jwt_expire_minutes
        self._refresh_token_expire_days = settings.user_jwt_refresh_expire_days

    def create_access_token(
        self, user_id: UUID, expires_delta: timedelta | None = None
    ) -> str:
        """
        Create a JWT access token for user.

        Args:
            user_id: The user ID to include in the token
            expires_delta: Optional custom expiration timedelta

        Returns:
            JWT access token string
        """
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self._access_token_expire_minutes
            )

        # Token payload following JWT standard claims
        payload = {
            "sub": str(user_id),  # Subject (user ID)
            "type": "access",  # Token type
            "exp": expire,  # Expiration time
            "iat": datetime.now(UTC),  # Issued at
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(
        self, user_id: UUID, expires_delta: timedelta | None = None
    ) -> str:
        """
        Create a JWT refresh token for user.

        Args:
            user_id: The user ID to include in the token
            expires_delta: Optional custom expiration timedelta

        Returns:
            JWT refresh token string
        """
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(days=self._refresh_token_expire_days)

        # Refresh token payload
        payload = {
            "sub": str(user_id),  # Subject (user ID)
            "type": "refresh",  # Token type
            "exp": expire,  # Expiration time
            "iat": datetime.now(UTC),  # Issued at
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string to verify

        Returns:
            Decoded token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError:
            return None

    def extract_user_id(self, token: str) -> UUID | None:
        """
        Extract user ID from a valid JWT token.

        Args:
            token: JWT token string

        Returns:
            User UUID if token is valid and contains user ID, None otherwise
        """
        payload = self.verify_token(token)
        if payload is None:
            return None

        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None

        try:
            return UUID(user_id_str)
        except ValueError:
            return None

    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired.

        Args:
            token: JWT token string

        Returns:
            True if token is expired, False if valid or invalid
        """
        payload = self.verify_token(token)
        if payload is None:
            return True

        exp = payload.get("exp")
        if exp is None:
            return True

        # Convert exp to datetime if it's a timestamp
        if isinstance(exp, int | float):
            exp_datetime = datetime.fromtimestamp(exp, tz=UTC)
        else:
            exp_datetime = exp

        return datetime.now(UTC) >= exp_datetime

    def get_token_expiry(self, token: str) -> datetime | None:
        """
        Get the expiry time of a token.

        Args:
            token: JWT token string

        Returns:
            Expiry datetime if token is valid, None otherwise
        """
        payload = self.verify_token(token)
        if payload is None:
            return None

        exp = payload.get("exp")
        if exp is None:
            return None

        # Convert exp to datetime if it's a timestamp
        if isinstance(exp, int | float):
            return datetime.fromtimestamp(exp, tz=UTC)
        else:
            return exp

    def get_token_type(self, token: str) -> str | None:
        """
        Get the type of a JWT token.

        Args:
            token: JWT token string

        Returns:
            Token type ("access" or "refresh") if valid, None otherwise
        """
        payload = self.verify_token(token)
        if payload is None:
            return None

        return payload.get("type")

    def refresh_access_token(self, refresh_token: str) -> str | None:
        """
        Create a new access token using a valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token if refresh token is valid, None otherwise
        """
        # Verify refresh token
        payload = self.verify_token(refresh_token)
        if payload is None:
            return None

        # Check if it's actually a refresh token
        if payload.get("type") != "refresh":
            return None

        # Extract user ID
        user_id = self.extract_user_id(refresh_token)
        if user_id is None:
            return None

        # Create new access token
        return self.create_access_token(user_id)
