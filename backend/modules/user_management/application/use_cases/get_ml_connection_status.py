"""
Get MercadoLibre connection status use case for user management module.

This use case retrieves and validates the user's MercadoLibre connection status.
"""

from uuid import UUID

from modules.user_management.domain.exceptions import ValidationError
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    ConnectionStatus,
    MLOAuthServiceProtocol,
)


class GetMLConnectionStatusUseCase:
    """
    Use case for getting MercadoLibre connection status.

    Retrieves and validates the user's ML connection health.
    """

    def __init__(self, oauth_service: MLOAuthServiceProtocol):
        """
        Initialize use case with OAuth service.

        Args:
            oauth_service: ML OAuth service implementation
        """
        self._oauth_service = oauth_service

    async def execute(self, user_id: UUID) -> ConnectionStatus:
        """
        Execute connection status check.

        Args:
            user_id: User UUID to check

        Returns:
            Connection status information

        Raises:
            ValidationError: If user ID is invalid
        """
        # Validate inputs
        if not user_id:
            raise ValidationError("User ID is required")

        # Get connection status
        return await self._oauth_service.get_connection_status(user_id)
