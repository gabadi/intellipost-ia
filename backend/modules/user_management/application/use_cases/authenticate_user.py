"""
Authenticate user use case.

This module contains the application use case for user authentication.
"""

from modules.user_management.domain.entities.user import User
from modules.user_management.domain.services.authentication import AuthenticationService


class AuthenticateUserUseCase:
    """Use case for authenticating a user."""

    def __init__(self, authentication_service: AuthenticationService):
        self._authentication_service = authentication_service

    async def execute(self, email: str, password: str) -> User | None:
        """Execute user authentication use case."""
        return await self._authentication_service.authenticate_user(email, password)
