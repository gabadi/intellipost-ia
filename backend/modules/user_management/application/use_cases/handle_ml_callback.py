"""
Handle MercadoLibre OAuth callback use case for user management module.

This use case handles the OAuth callback and token exchange
with manager account validation.
"""

from uuid import UUID

from modules.user_management.domain.entities.ml_credentials import MLCredentials
from modules.user_management.domain.exceptions import ValidationError
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    MLOAuthServiceProtocol,
)


class HandleMLCallbackUseCase:
    """
    Use case for handling MercadoLibre OAuth callback.
    
    Processes the OAuth callback, validates PKCE parameters,
    exchanges code for tokens, and validates manager account.
    """

    def __init__(self, oauth_service: MLOAuthServiceProtocol):
        """
        Initialize use case with OAuth service.
        
        Args:
            oauth_service: ML OAuth service implementation
        """
        self._oauth_service = oauth_service

    async def execute(
        self,
        user_id: UUID,
        code: str,
        state: str,
        code_verifier: str,
    ) -> MLCredentials:
        """
        Execute OAuth callback handling.
        
        Args:
            user_id: User UUID completing the flow
            code: Authorization code from callback
            state: CSRF state parameter
            code_verifier: PKCE code verifier
            
        Returns:
            ML credentials entity with tokens
            
        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If OAuth fails or account is not manager
        """
        # Validate inputs
        if not user_id:
            raise ValidationError("User ID is required")
        
        if not code:
            raise ValidationError("Authorization code is required")
        
        if len(code) < 10:
            raise ValidationError("Authorization code is too short")
        
        if not state:
            raise ValidationError("State parameter is required")
        
        if len(state) < 10:
            raise ValidationError("State parameter is too short")
        
        if not code_verifier:
            raise ValidationError("Code verifier is required")
        
        if len(code_verifier) < 43 or len(code_verifier) > 128:
            raise ValidationError("Code verifier must be 43-128 characters long")
        
        # Handle OAuth callback
        return await self._oauth_service.handle_oauth_callback(
            user_id=user_id,
            code=code,
            state=state,
            code_verifier=code_verifier,
        )