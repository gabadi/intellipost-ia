"""
JWT token service implementation.

This module provides JWT token creation, validation, and refresh functionality
following the authentication requirements from Epic 6, Story 1.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from pydantic import BaseModel

from infrastructure.config.settings import Settings


class TokenPair(BaseModel):
    """Token pair containing access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthenticatedUser(BaseModel):
    """Authenticated user information from JWT token."""

    user_id: UUID
    email: str
    is_active: bool
    exp: int  # Token expiration timestamp


class JWTService:
    """
    JWT token service for authentication.

    Handles creation, validation, and refresh of JWT tokens using HS256 algorithm.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize JWT service with configuration.

        Args:
            settings: Application settings containing JWT configuration
        """
        self.settings = settings
        self.algorithm = "HS256"  # HS256 as specified in story requirements
        self.access_token_expire_minutes = 15  # 15 minutes as per story requirements
        self.refresh_token_expire_days = 7  # 7 days as per story requirements

    def create_token_pair(
        self, user_id: UUID, email: str, is_active: bool
    ) -> TokenPair:
        """
        Create access and refresh token pair for user.

        Args:
            user_id: User's unique identifier
            email: User's email address
            is_active: User's active status

        Returns:
            TokenPair: Access and refresh tokens with expiry information

        Raises:
            ValueError: If required parameters are missing
        """
        if not user_id or not email:
            raise ValueError("User ID and email are required")

        # Create access token
        access_token_expires = datetime.now(UTC) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        access_token_data = {
            "sub": str(user_id),
            "email": email,
            "is_active": is_active,
            "exp": access_token_expires,
            "type": "access",
            "iat": datetime.now(UTC),
        }
        access_token = jwt.encode(
            access_token_data,
            self.settings.jwt_secret_key,
            algorithm=self.algorithm,
        )

        # Create refresh token
        refresh_token_expires = datetime.now(UTC) + timedelta(
            days=self.refresh_token_expire_days
        )
        refresh_token_data = {
            "sub": str(user_id),
            "email": email,
            "is_active": is_active,
            "exp": refresh_token_expires,
            "type": "refresh",
            "iat": datetime.now(UTC),
        }
        refresh_token = jwt.encode(
            refresh_token_data,
            self.settings.jwt_secret_key,
            algorithm=self.algorithm,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60,  # Convert to seconds
        )

    def validate_access_token(self, token: str) -> AuthenticatedUser:
        """
        Validate and decode an access token.

        Args:
            token: JWT access token to validate

        Returns:
            AuthenticatedUser: Decoded user information

        Raises:
            JWTError: If token is invalid, expired, or malformed
            ValueError: If token type is not 'access'
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.algorithm],
            )

            # Verify token type
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")

            # Extract user information
            user_id = UUID(payload.get("sub"))
            email = payload.get("email")
            is_active = payload.get("is_active", False)
            exp = payload.get("exp")

            if not user_id or not email or exp is None:
                raise ValueError("Invalid token payload")

            return AuthenticatedUser(
                user_id=user_id,
                email=email,
                is_active=is_active,
                exp=exp,
            )

        except JWTError as e:
            raise JWTError(f"Token validation failed: {str(e)}") from e
        except (ValueError, TypeError) as e:
            raise JWTError(f"Invalid token format: {str(e)}") from e

    def validate_refresh_token(self, token: str) -> AuthenticatedUser:
        """
        Validate and decode a refresh token.

        Args:
            token: JWT refresh token to validate

        Returns:
            AuthenticatedUser: Decoded user information

        Raises:
            JWTError: If token is invalid, expired, or malformed
            ValueError: If token type is not 'refresh'
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.algorithm],
            )

            # Verify token type
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")

            # Extract user information
            user_id = UUID(payload.get("sub"))
            email = payload.get("email")
            is_active = payload.get("is_active", False)
            exp = payload.get("exp")

            if not user_id or not email or exp is None:
                raise ValueError("Invalid token payload")

            return AuthenticatedUser(
                user_id=user_id,
                email=email,
                is_active=is_active,
                exp=exp,
            )

        except JWTError as e:
            raise JWTError(f"Refresh token validation failed: {str(e)}") from e
        except (ValueError, TypeError) as e:
            raise JWTError(f"Invalid refresh token format: {str(e)}") from e

    def create_access_token_from_refresh(self, refresh_token: str) -> str:
        """
        Create a new access token from a valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            str: New access token

        Raises:
            JWTError: If refresh token is invalid or expired
        """
        # Validate refresh token
        user_info = self.validate_refresh_token(refresh_token)

        # Create new access token
        access_token_expires = datetime.now(UTC) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        access_token_data = {
            "sub": str(user_info.user_id),
            "email": user_info.email,
            "is_active": user_info.is_active,
            "exp": access_token_expires,
            "type": "access",
            "iat": datetime.now(UTC),
        }

        return jwt.encode(
            access_token_data,
            self.settings.jwt_secret_key,
            algorithm=self.algorithm,
        )

    def decode_token_payload(self, token: str) -> dict[str, Any]:
        """
        Decode token payload without validation (for debugging).

        Args:
            token: JWT token to decode

        Returns:
            Dict[str, Any]: Token payload

        Raises:
            JWTError: If token format is invalid
        """
        try:
            return jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},  # Skip expiration check for debugging
            )
        except JWTError as e:
            raise JWTError(f"Token decode failed: {str(e)}") from e

    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired without full validation.

        Args:
            token: JWT token to check

        Returns:
            bool: True if token is expired, False otherwise
        """
        try:
            payload = self.decode_token_payload(token)
            exp_timestamp = payload.get("exp")

            if exp_timestamp is None:
                return True

            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=UTC)
            return datetime.now(UTC) > exp_datetime

        except JWTError:
            return True  # Consider invalid tokens as expired
