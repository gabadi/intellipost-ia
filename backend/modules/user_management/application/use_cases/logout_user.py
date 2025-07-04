"""
Logout user use case.

This module contains the application use case for user logout.
"""

import hashlib

from modules.user_management.domain.ports.jwt_service_protocol import JWTServiceProtocol
from modules.user_management.domain.ports.refresh_token_repository_protocol import (
    RefreshTokenRepositoryProtocol,
)


class LogoutUserUseCase:
    """Use case for logging out a user and invalidating tokens."""

    def __init__(
        self,
        jwt_service: JWTServiceProtocol,
        refresh_token_repository: RefreshTokenRepositoryProtocol,
    ):
        self._jwt_service = jwt_service
        self._refresh_token_repository = refresh_token_repository

    async def execute(
        self, refresh_token: str | None = None, access_token: str | None = None
    ) -> bool:
        """
        Logout user by invalidating refresh tokens.

        Args:
            refresh_token: Optional refresh token to invalidate
            access_token: Optional access token to extract user ID for logout

        Returns:
            True if logout was successful, False otherwise
        """
        user_id = None

        # Extract user ID from either token
        if access_token:
            user_id = self._jwt_service.extract_user_id(access_token)
        elif refresh_token:
            user_id = self._jwt_service.extract_user_id(refresh_token)

        if user_id is None:
            return False

        # If specific refresh token provided, invalidate only that token
        if refresh_token:
            refresh_token_hash = self._hash_token(refresh_token)
            await self._refresh_token_repository.delete_by_token_hash(
                refresh_token_hash
            )
        else:
            # Otherwise, invalidate all refresh tokens for the user (logout from all devices)
            await self._refresh_token_repository.delete_by_user_id(user_id)

        # Note: Access tokens cannot be invalidated server-side with JWT
        # They will expire naturally based on their expiry time

        return True

    def _hash_token(self, token: str) -> str:
        """Hash a refresh token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
