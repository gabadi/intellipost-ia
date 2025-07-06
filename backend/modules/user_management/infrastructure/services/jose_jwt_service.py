"""
JOSE (python-jose) implementation of JWTServiceProtocol.

This module provides JWT token operations using python-jose library.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt


class JoseJWTService:
    """JOSE implementation of JWTServiceProtocol."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ):
        """Initialize JWT service with configuration."""
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self, user_id: UUID, expires_delta: datetime | None = None
    ) -> str:
        """Create a JWT access token for user."""
        if expires_delta:
            expire = expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access",
            "iat": datetime.now(UTC),
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a JWT refresh token for user."""
        expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
            "iat": datetime.now(UTC),
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def extract_user_id(self, token: str) -> UUID | None:
        """Extract user ID from a valid JWT token."""
        payload = self.verify_token(token)
        if payload and "sub" in payload:
            try:
                return UUID(payload["sub"])
            except (ValueError, TypeError):
                return None
        return None
