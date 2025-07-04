"""
Register user use case.

This module contains the application use case for user registration.
"""

from modules.user_management.application.use_cases.generate_tokens import (
    GenerateTokensUseCase,
    TokenPair,
)
from modules.user_management.domain.entities.user import User
from modules.user_management.domain.services.authentication import AuthenticationService


class UserRegistrationResult:
    """Result of user registration containing user and tokens."""

    def __init__(self, user: User, tokens: TokenPair):
        self.user = user
        self.tokens = tokens


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(
        self,
        authentication_service: AuthenticationService,
        generate_tokens_use_case: GenerateTokensUseCase,
    ):
        self._authentication_service = authentication_service
        self._generate_tokens_use_case = generate_tokens_use_case

    async def execute(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> UserRegistrationResult:
        """
        Execute user registration use case.

        Args:
            email: User email address
            password: User password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            UserRegistrationResult containing user and JWT tokens
        """
        # Register user through authentication service
        user = await self._authentication_service.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Generate JWT tokens for immediate login
        tokens = await self._generate_tokens_use_case.execute(user)

        return UserRegistrationResult(user=user, tokens=tokens)
