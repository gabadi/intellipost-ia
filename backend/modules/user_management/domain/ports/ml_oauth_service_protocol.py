"""
MercadoLibre OAuth Service Protocol for user management module.

This module defines the protocol for ML OAuth service operations
following the hexagonal architecture pattern.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from modules.user_management.domain.entities.ml_credentials import MLCredentials


@dataclass
class OAuthFlowData:
    """Data class for OAuth flow initiation."""

    authorization_url: str
    state: str
    code_verifier: str
    code_challenge: str
    site_id: str
    redirect_uri: str


@dataclass
class ConnectionStatus:
    """Data class for connection status information."""

    is_connected: bool
    connection_health: str  # "healthy", "expired", "invalid", "disconnected"
    ml_nickname: str | None = None
    ml_email: str | None = None
    ml_site_id: str | None = None
    expires_at: datetime | None = None
    last_validated_at: datetime | None = None
    error_message: str | None = None


class MLOAuthServiceProtocol(Protocol):
    """
    Protocol for MercadoLibre OAuth service operations.

    Defines the interface for ML OAuth operations following
    the hexagonal architecture pattern and protocol-based design.
    """

    async def initiate_oauth_flow(
        self,
        user_id: UUID,
        redirect_uri: str,
        site_id: str = "MLA",
    ) -> OAuthFlowData:
        """
        Initiate OAuth 2.0 flow with PKCE.

        Args:
            user_id: User UUID initiating the flow
            redirect_uri: OAuth redirect URI
            site_id: MercadoLibre site ID (MLA, MLM, MBL, MLC, MCO)

        Returns:
            OAuth flow data including authorization URL and PKCE parameters

        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If user is not found
        """
        ...

    async def handle_oauth_callback(
        self,
        user_id: UUID,
        code: str,
        state: str,
        code_verifier: str,
    ) -> MLCredentials:
        """
        Handle OAuth callback and exchange code for tokens.

        CRITICAL: Implements manager account validation and PKCE verification.

        Args:
            user_id: User UUID completing the flow
            code: Authorization code from callback
            state: CSRF state parameter
            code_verifier: PKCE code verifier

        Returns:
            ML credentials entity with tokens

        Raises:
            ValidationError: If parameters are invalid or PKCE fails
            AuthenticationError: If code exchange fails
            MLManagerAccountError: If account is not a manager account
        """
        ...

    async def refresh_token(
        self,
        credentials: MLCredentials,
    ) -> MLCredentials:
        """
        Refresh access token using refresh token.

        CRITICAL: Implements single-use refresh token requirement.
        Each refresh generates new access + refresh tokens.

        Args:
            credentials: Current ML credentials

        Returns:
            Updated ML credentials with new tokens

        Raises:
            AuthenticationError: If token refresh fails
        """
        ...

    async def validate_connection(
        self,
        credentials: MLCredentials,
    ) -> ConnectionStatus:
        """
        Validate connection health and token validity.

        Args:
            credentials: ML credentials to validate

        Returns:
            Connection status information

        Raises:
            AuthenticationError: If validation fails
        """
        ...

    async def disconnect(
        self,
        user_id: UUID,
    ) -> bool:
        """
        Disconnect MercadoLibre integration for user.

        Args:
            user_id: User UUID to disconnect

        Returns:
            True if disconnection successful, False if not connected

        Raises:
            AuthenticationError: If user is not found
        """
        ...

    async def get_connection_status(
        self,
        user_id: UUID,
    ) -> ConnectionStatus:
        """
        Get connection status for user.

        Args:
            user_id: User UUID to check

        Returns:
            Connection status information

        Raises:
            AuthenticationError: If user is not found
        """
        ...

    async def schedule_token_refresh(
        self,
        credentials: MLCredentials,
    ) -> bool:
        """
        Schedule automatic token refresh at 5.5 hours.

        Args:
            credentials: ML credentials to schedule refresh for

        Returns:
            True if scheduling successful, False otherwise
        """
        ...

    async def process_expired_tokens(self) -> int:
        """
        Process and refresh expired tokens.

        Used by background tasks to refresh tokens before expiry.

        Returns:
            Number of tokens processed
        """
        ...

    async def validate_manager_account(
        self,
        access_token: str,
    ) -> bool:
        """
        Validate that the account is a manager account.

        CRITICAL: Only manager accounts can authorize applications.

        Args:
            access_token: ML access token

        Returns:
            True if manager account, False if collaborator

        Raises:
            AuthenticationError: If validation fails
        """
        ...

    async def generate_pkce_parameters(self) -> tuple[str, str]:
        """
        Generate PKCE code verifier and challenge.

        CRITICAL: Implements PKCE security requirement (SHA-256 method).

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        ...

    async def validate_state_parameter(
        self,
        state: str,
        user_id: UUID,
    ) -> bool:
        """
        Validate CSRF state parameter.

        Args:
            state: State parameter from callback
            user_id: User UUID

        Returns:
            True if state is valid, False otherwise
        """
        ...

    async def get_user_credentials(
        self,
        user_id: UUID,
    ) -> MLCredentials | None:
        """
        Get ML credentials for user.

        Args:
            user_id: User UUID

        Returns:
            ML credentials if found, None otherwise
        """
        ...

    async def update_user_info(
        self,
        credentials: MLCredentials,
        access_token: str,
    ) -> MLCredentials:
        """
        Update user information from MercadoLibre API.

        Args:
            credentials: ML credentials to update
            access_token: ML access token

        Returns:
            Updated ML credentials

        Raises:
            AuthenticationError: If API call fails
        """
        ...
