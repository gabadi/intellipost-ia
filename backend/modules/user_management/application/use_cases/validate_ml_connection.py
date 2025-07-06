"""
Validate MercadoLibre connection use case for user management module.

This use case handles connection health validation and token checking.
"""

from uuid import UUID

from modules.user_management.domain.exceptions import (
    AuthenticationError,
    ValidationError,
)
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    ConnectionStatus,
    MLOAuthServiceProtocol,
)


class ValidateMLConnectionUseCase:
    """
    Use case for validating MercadoLibre connection health.
    
    Checks token validity, connection status, and performs
    automatic refresh if needed.
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
        Execute connection validation.
        
        Args:
            user_id: User UUID to validate connection for
            
        Returns:
            Connection status with health information
            
        Raises:
            ValidationError: If user ID is invalid
            AuthenticationError: If user is not found
        """
        # Validate inputs
        if not user_id:
            raise ValidationError("User ID is required")
        
        # Get user credentials
        credentials = await self._oauth_service.get_user_credentials(user_id)
        if not credentials:
            return ConnectionStatus(
                is_connected=False,
                connection_health="disconnected",
                error_message="No MercadoLibre connection found",
            )
        
        # Validate connection
        return await self._oauth_service.validate_connection(credentials)