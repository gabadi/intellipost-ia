"""
Authenticate user use case.

This module contains the application use case for user authentication.
"""

from modules.user_management.application.use_cases.generate_tokens import (
    GenerateTokensUseCase,
    TokenPair,
)
from modules.user_management.domain.entities.user import User
from modules.user_management.domain.services.authentication import AuthenticationService


class UserAuthenticationResult:
    """Result of user authentication containing user and tokens."""

    def __init__(self, user: User, tokens: TokenPair):
        self.user = user
        self.tokens = tokens


class AuthenticateUserUseCase:
    """Use case for authenticating a user."""

    def __init__(
        self,
        authentication_service: AuthenticationService,
        generate_tokens_use_case: GenerateTokensUseCase,
    ):
        self._authentication_service = authentication_service
        self._generate_tokens_use_case = generate_tokens_use_case

    async def execute(
        self, email: str, password: str
    ) -> UserAuthenticationResult | None:
        """
        Execute user authentication use case.

        Args:
            email: User email address
            password: User password

        Returns:
            UserAuthenticationResult containing user and JWT tokens if successful, None if failed
        """
        # Authenticate user credentials
        user = await self._authentication_service.authenticate_user(email, password)

        if user is None:
            return None

        # Generate JWT tokens for successful login
        tokens = await self._generate_tokens_use_case.execute(user)

        return UserAuthenticationResult(user=user, tokens=tokens)
