"""
Disconnect MercadoLibre OAuth use case for user management module.

This use case handles disconnecting the user's MercadoLibre integration.
"""

from uuid import UUID

from modules.user_management.domain.exceptions import ValidationError
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    MLOAuthServiceProtocol,
)


class DisconnectMLUseCase:
    """
    Use case for disconnecting MercadoLibre integration.

    Removes the user's MercadoLibre credentials and connection.
    """

    def __init__(self, oauth_service: MLOAuthServiceProtocol):
        """
        Initialize use case with OAuth service.

        Args:
            oauth_service: ML OAuth service implementation
        """
        self._oauth_service = oauth_service

    async def execute(self, user_id: UUID) -> bool:
        """
        Execute ML disconnection.

        Args:
            user_id: User UUID to disconnect

        Returns:
            True if disconnection successful, False if not connected

        Raises:
            ValidationError: If user ID is invalid
        """
        # Validate inputs
        if not user_id:
            raise ValidationError("User ID is required")

        # Disconnect ML integration
        return await self._oauth_service.disconnect(user_id)
