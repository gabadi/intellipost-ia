"""
Refresh token use case.

This module contains the application use case for JWT token refresh.
"""

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from modules.user_management.application.use_cases.generate_tokens import TokenPair
from modules.user_management.domain.entities.refresh_token import RefreshToken
from modules.user_management.domain.entities.user import User
from modules.user_management.domain.ports.jwt_service_protocol import JWTServiceProtocol
from modules.user_management.domain.ports.refresh_token_repository_protocol import (
    RefreshTokenRepositoryProtocol,
)
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)


class RefreshTokenResult:
    """Result of token refresh containing tokens and user."""

    def __init__(self, tokens: TokenPair, user: User):
        self.tokens = tokens
        self.user = user


class RefreshTokenUseCase:
    """Use case for refreshing JWT access tokens."""

    def __init__(
        self,
        jwt_service: JWTServiceProtocol,
        refresh_token_repository: RefreshTokenRepositoryProtocol,
        user_repository: UserRepositoryProtocol,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ):
        self._jwt_service = jwt_service
        self._refresh_token_repository = refresh_token_repository
        self._user_repository = user_repository
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    async def execute(self, refresh_token: str) -> RefreshTokenResult | None:
        """
        Refresh JWT access token using refresh token.

        Args:
            refresh_token: Valid refresh token string

        Returns:
            RefreshTokenResult containing new tokens and user if valid, None otherwise
        """
        # Verify refresh token format and extract user ID
        user_id = self._jwt_service.extract_user_id(refresh_token)
        if user_id is None:
            return None

        # Check if token is expired
        if self._jwt_service.is_token_expired(refresh_token):
            return None

        # Verify refresh token exists in database
        refresh_token_hash = self._hash_token(refresh_token)
        stored_token = await self._refresh_token_repository.get_by_token_hash(
            refresh_token_hash
        )

        if stored_token is None or stored_token.is_expired():
            return None

        # Get user to ensure they still exist and are active
        user = await self._user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            return None

        # Delete old refresh token for security (rotation)
        await self._refresh_token_repository.delete_by_token_hash(refresh_token_hash)

        # Generate new token pair
        new_access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            expires_delta=timedelta(minutes=self._access_token_expire_minutes),
        )

        new_refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
            expires_delta=timedelta(days=self._refresh_token_expire_days),
        )

        # Store new refresh token
        new_refresh_token_hash = self._hash_token(new_refresh_token)
        new_refresh_token_entity = RefreshToken(
            id=uuid4(),
            user_id=user.id,
            token_hash=new_refresh_token_hash,
            expires_at=datetime.now(UTC)
            + timedelta(days=self._refresh_token_expire_days),
            created_at=datetime.now(UTC),
        )

        await self._refresh_token_repository.create(new_refresh_token_entity)

        new_tokens = TokenPair(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=self._access_token_expire_minutes * 60,
        )

        return RefreshTokenResult(tokens=new_tokens, user=user)

    def _hash_token(self, token: str) -> str:
        """Hash a refresh token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
