"""
Initiate MercadoLibre OAuth use case for user management module.

This use case handles the initiation of the ML OAuth 2.0 flow
with PKCE security.
"""

from uuid import UUID

from modules.user_management.domain.exceptions import ValidationError
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    MLOAuthServiceProtocol,
    OAuthFlowData,
)


class InitiateMLOAuthUseCase:
    """
    Use case for initiating MercadoLibre OAuth flow.

    Handles the first step of the OAuth 2.0 flow by generating
    authorization URL with PKCE parameters.
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
        redirect_uri: str,
        site_id: str = "MLA",
    ) -> OAuthFlowData:
        """
        Execute OAuth flow initiation.

        Args:
            user_id: User UUID initiating the flow
            redirect_uri: OAuth redirect URI
            site_id: MercadoLibre site ID

        Returns:
            OAuth flow data including authorization URL

        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate inputs
        if not user_id:
            raise ValidationError("User ID is required")

        if not redirect_uri:
            raise ValidationError("Redirect URI is required")

        if not redirect_uri.startswith(("http://", "https://")):
            raise ValidationError("Redirect URI must be a valid HTTP/HTTPS URL")

        valid_sites = {"MLA", "MLM", "MBL", "MLC", "MCO"}
        if site_id not in valid_sites:
            raise ValidationError(f"Invalid site_id. Must be one of: {valid_sites}")

        # Initiate OAuth flow
        return await self._oauth_service.initiate_oauth_flow(
            user_id=user_id,
            redirect_uri=redirect_uri,
            site_id=site_id,
        )
