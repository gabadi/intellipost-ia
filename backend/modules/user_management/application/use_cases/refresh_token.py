"""
Refresh token use case.

This module contains the application use case for JWT token refresh.
"""

from modules.user_management.domain.entities.user import User
from modules.user_management.domain.exceptions import (
    InvalidTokenError,
    UserNotFoundError,
)
from modules.user_management.domain.ports.jwt_service_protocol import JWTServiceProtocol
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)


class RefreshTokenUseCase:
    """Use case for refreshing JWT tokens."""

    def __init__(
        self,
        jwt_service: JWTServiceProtocol,
        user_repository: UserRepositoryProtocol,
    ):
        self._jwt_service = jwt_service
        self._user_repository = user_repository

    async def execute(self, refresh_token: str) -> tuple[str, str, User]:
        """
        Execute token refresh use case.

        Returns:
            Tuple of (new_access_token, new_refresh_token, user)
        """
        # Verify the refresh token
        payload = self._jwt_service.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidTokenError("refresh")

        # Extract user ID
        user_id = self._jwt_service.extract_user_id(refresh_token)
        if not user_id:
            raise InvalidTokenError("refresh")

        # Get user from repository
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))

        # Check if user is still active
        if not user.is_active:
            raise InvalidTokenError("refresh")

        # Generate new tokens
        new_access_token = self._jwt_service.create_access_token(user.id)
        new_refresh_token = self._jwt_service.create_refresh_token(user.id)

        return new_access_token, new_refresh_token, user
