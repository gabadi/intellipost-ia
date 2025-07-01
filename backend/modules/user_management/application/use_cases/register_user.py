"""
Register user use case.

This module contains the application use case for user registration.
"""

from modules.user_management.domain.entities.user import User
from modules.user_management.domain.services.authentication import AuthenticationService


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(self, authentication_service: AuthenticationService):
        self._authentication_service = authentication_service

    async def execute(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Execute user registration use case."""
        return await self._authentication_service.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
