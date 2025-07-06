"""
Authenticate user use case.

This module contains the application use case for user authentication.
"""

from modules.user_management.domain.entities.user import User
from modules.user_management.domain.exceptions import InvalidCredentialsError
from modules.user_management.domain.ports.jwt_service_protocol import JWTServiceProtocol
from modules.user_management.domain.services.authentication import AuthenticationService


class AuthenticateUserUseCase:
    """Use case for user authentication."""

    def __init__(
        self,
        authentication_service: AuthenticationService,
        jwt_service: JWTServiceProtocol,
    ):
        self._authentication_service = authentication_service
        self._jwt_service = jwt_service

    async def execute(self, email: str, password: str) -> tuple[str, str, User]:
        """
        Execute user authentication use case.

        Returns:
            Tuple of (access_token, refresh_token, user)
        """
        # Authenticate user
        user = await self._authentication_service.authenticate_user(email, password)
        if not user:
            raise InvalidCredentialsError()

        # Generate JWT tokens
        access_token = self._jwt_service.create_access_token(user.id)
        refresh_token = self._jwt_service.create_refresh_token(user.id)

        return access_token, refresh_token, user
