"""
Refresh MercadoLibre token use case for user management module.

This use case handles refreshing ML access tokens using refresh tokens.
"""

from uuid import UUID

from modules.user_management.domain.entities.ml_credentials import MLCredentials
from modules.user_management.domain.exceptions import (
    AuthenticationError,
    ValidationError,
)
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    MLOAuthServiceProtocol,
)


class RefreshMLTokenUseCase:
    """
    Use case for refreshing MercadoLibre access tokens.

    Implements the automatic token refresh at 5.5 hours
    with single-use refresh token handling.
    """

    def __init__(self, oauth_service: MLOAuthServiceProtocol):
        """
        Initialize use case with OAuth service.

        Args:
            oauth_service: ML OAuth service implementation
        """
        self._oauth_service = oauth_service

    async def execute(self, user_id: UUID) -> MLCredentials:
        """
        Execute token refresh.

        Args:
            user_id: User UUID to refresh tokens for

        Returns:
            Updated ML credentials with new tokens

        Raises:
            ValidationError: If user ID is invalid
            AuthenticationError: If refresh fails or user not connected
        """
        # Validate inputs
        if not user_id:
            raise ValidationError("User ID is required")

        # Get current credentials
        credentials = await self._oauth_service.get_user_credentials(user_id)
        if not credentials:
            raise AuthenticationError("User is not connected to MercadoLibre")

        # Check if refresh is needed
        if not credentials.should_refresh_token:
            return credentials

        # Check if refresh token is expired
        if credentials.is_refresh_token_expired:
            raise AuthenticationError(
                "Refresh token has expired, reconnection required"
            )

        # Refresh tokens
        return await self._oauth_service.refresh_token(credentials)
