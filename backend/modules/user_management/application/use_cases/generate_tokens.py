"""
Generate tokens use case.

This module contains the application use case for JWT token generation.
"""

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from modules.user_management.domain.entities.refresh_token import RefreshToken
from modules.user_management.domain.entities.user import User
from modules.user_management.domain.ports.jwt_service_protocol import JWTServiceProtocol
from modules.user_management.domain.ports.refresh_token_repository_protocol import (
    RefreshTokenRepositoryProtocol,
)


class TokenPair:
    """Token pair containing access and refresh tokens."""

    def __init__(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in


class GenerateTokensUseCase:
    """Use case for generating JWT access and refresh tokens."""

    def __init__(
        self,
        jwt_service: JWTServiceProtocol,
        refresh_token_repository: RefreshTokenRepositoryProtocol,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ):
        self._jwt_service = jwt_service
        self._refresh_token_repository = refresh_token_repository
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    async def execute(self, user: User) -> TokenPair:
        """
        Generate JWT access and refresh tokens for user.

        Args:
            user: User entity to generate tokens for

        Returns:
            TokenPair containing access and refresh tokens
        """
        # Create access token with mobile-optimized expiry (15 minutes)
        access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            expires_delta=timedelta(minutes=self._access_token_expire_minutes),
        )

        # Create refresh token with 7-day expiry for user convenience
        refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
            expires_delta=timedelta(days=self._refresh_token_expire_days),
        )

        # Store refresh token hash in database for security
        refresh_token_hash = self._hash_token(refresh_token)
        refresh_token_entity = RefreshToken(
            id=uuid4(),
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.now(UTC)
            + timedelta(days=self._refresh_token_expire_days),
            created_at=datetime.now(UTC),
        )

        await self._refresh_token_repository.create(refresh_token_entity)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._access_token_expire_minutes * 60,  # Convert to seconds
        )

    def _hash_token(self, token: str) -> str:
        """Hash a refresh token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
