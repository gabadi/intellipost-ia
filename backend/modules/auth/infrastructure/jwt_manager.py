"""
JWT token management utilities.

This module provides JWT token generation and validation for authentication.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from infrastructure.config.settings import settings

from .token_blacklist import token_blacklist


class JWTManager:
    """Manages JWT token creation and validation."""

    @staticmethod
    def create_access_token(user_id: UUID, email: str) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User UUID
            email: User email

        Returns:
            JWT access token string
        """
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        data = {"sub": str(user_id), "email": email, "exp": expire, "type": "access"}
        return jwt.encode(data, settings.secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def create_refresh_token(user_id: UUID) -> tuple[str, datetime]:
        """
        Create a JWT refresh token.

        Args:
            user_id: User UUID

        Returns:
            Tuple of (refresh token, expiration datetime)
        """
        expire = datetime.now(UTC) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        data = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        token = jwt.encode(data, settings.secret_key, algorithm=settings.jwt_algorithm)
        return token, expire

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            raise

    @staticmethod
    async def validate_access_token(token: str) -> dict[str, Any]:
        """
        Validate an access token and return its payload.

        Args:
            token: JWT access token

        Returns:
            Token payload if valid

        Raises:
            JWTError: If token is invalid, expired, blacklisted, or not an access token
        """
        # Check if token is blacklisted
        if await token_blacklist.is_token_blacklisted(token, "access"):
            raise JWTError("Token has been revoked")

        payload = JWTManager.decode_token(token)
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        return payload

    @staticmethod
    async def validate_refresh_token(token: str) -> dict[str, Any]:
        """
        Validate a refresh token and return its payload.

        Args:
            token: JWT refresh token

        Returns:
            Token payload if valid

        Raises:
            JWTError: If token is invalid, expired, blacklisted, or not a refresh token
        """
        # Check if token is blacklisted
        if await token_blacklist.is_token_blacklisted(token, "refresh"):
            raise JWTError("Token has been revoked")

        payload = JWTManager.decode_token(token)
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
        return payload
