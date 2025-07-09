"""
MercadoLibre OAuth Service for user management module.

This service implements the ML OAuth 2.0 flow with PKCE security,
manager account validation, and automatic token refresh.
"""

import base64
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from modules.user_management.domain.entities.ml_credentials import MLCredentials
from modules.user_management.domain.exceptions import (
    AuthenticationError,
    ValidationError,
)
from modules.user_management.domain.ports.ml_credentials_repository_protocol import (
    MLCredentialsRepositoryProtocol,
)
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    ConnectionStatus,
    MLOAuthServiceProtocol,
    OAuthFlowData,
)
from modules.user_management.infrastructure.services.credential_encryption_service import (
    CredentialEncryptionService,
)
from modules.user_management.infrastructure.services.mercadolibre_api_client import (
    MercadoLibreAPIClient,
    MLManagerAccountError,
    MLOAuthError,
    MLRateLimitError,
)


class MLOAuthService(MLOAuthServiceProtocol):
    """
    MercadoLibre OAuth service implementation.

    Implements the complete OAuth 2.0 flow with PKCE security,
    manager account validation, and token management as specified
    in Epic 6 Story 2.
    """

    def __init__(
        self,
        ml_client: MercadoLibreAPIClient,
        credentials_repository: MLCredentialsRepositoryProtocol,
        encryption_service: CredentialEncryptionService,
        app_id: str,
        app_secret: str,
    ):
        """
        Initialize OAuth service.

        Args:
            ml_client: MercadoLibre API client
            credentials_repository: ML credentials repository
            encryption_service: Credential encryption service
            app_id: MercadoLibre app ID
            app_secret: MercadoLibre app secret
        """
        self._ml_client = ml_client
        self._credentials_repository = credentials_repository
        self._encryption_service = encryption_service
        self._app_id = app_id
        self._app_secret = app_secret

        # State storage for CSRF protection (in production, use Redis/cache)
        self._state_storage: dict[str, dict[str, Any]] = {}

    async def initiate_oauth_flow(
        self,
        user_id: UUID,
        redirect_uri: str,
        site_id: str = "MLA",
    ) -> OAuthFlowData:
        """Initiate OAuth 2.0 flow with PKCE."""
        # Validate site_id
        valid_sites = {"MLA", "MLM", "MBL", "MLC", "MCO"}
        if site_id not in valid_sites:
            raise ValidationError(f"Invalid site_id: {site_id}")

        # Validate redirect_uri
        if not redirect_uri or not redirect_uri.startswith(("http://", "https://")):
            raise ValidationError("Invalid redirect_uri")

        # Generate PKCE parameters
        code_verifier, code_challenge = await self.generate_pkce_parameters()

        # Generate CSRF state
        state = secrets.token_urlsafe(32)

        # Store state and parameters for validation
        self._state_storage[state] = {
            "user_id": str(user_id),
            "code_verifier": code_verifier,
            "site_id": site_id,
            "redirect_uri": redirect_uri,
            "created_at": datetime.now(UTC),
        }

        # Build authorization URL
        auth_url = self._ml_client.build_auth_url(
            site_id=site_id,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
        )

        return OAuthFlowData(
            authorization_url=auth_url,
            state=state,
            code_verifier=code_verifier,
            code_challenge=code_challenge,
            site_id=site_id,
            redirect_uri=redirect_uri,
        )

    async def handle_oauth_callback(
        self,
        user_id: UUID,
        code: str,
        state: str,
        code_verifier: str,
    ) -> MLCredentials:
        """Handle OAuth callback and exchange code for tokens."""
        # Validate state parameter (CSRF protection)
        if not await self.validate_state_parameter(state, user_id):
            raise ValidationError("Invalid state parameter")

        # Get stored parameters
        state_data = self._state_storage.get(state)
        if not state_data:
            raise ValidationError("State parameter not found")

        # Clean up state storage
        del self._state_storage[state]

        site_id = state_data["site_id"]
        redirect_uri = state_data["redirect_uri"]

        try:
            # Exchange code for tokens
            token_response = await self._ml_client.exchange_code_for_tokens(
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier,
            )

            access_token = token_response["access_token"]
            refresh_token = token_response["refresh_token"]
            expires_in = token_response["expires_in"]  # 21600 seconds (6 hours)
            ml_user_id = token_response["user_id"]

            # CRITICAL: Validate manager account
            is_manager = await self.validate_manager_account(access_token)
            if not is_manager:
                raise MLManagerAccountError(
                    "Only manager accounts can authorize applications. "
                    "Collaborator accounts cannot connect to IntelliPost AI."
                )

            # Get user information
            user_info = await self._ml_client.get_user_info(access_token)

            # Calculate expiration times
            expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
            refresh_expires_at = datetime.now(UTC) + timedelta(days=180)  # 6 months

            # Encrypt tokens
            encrypted_access_token = self._encryption_service.encrypt_access_token(
                access_token
            )
            encrypted_refresh_token = self._encryption_service.encrypt_refresh_token(
                refresh_token
            )
            encrypted_app_secret = self._encryption_service.encrypt_app_secret(
                self._app_secret
            )

            # Create ML credentials
            credentials = MLCredentials(
                id=uuid4(),
                user_id=user_id,
                ml_app_id=self._app_id,
                ml_secret_key_encrypted=encrypted_app_secret,
                ml_access_token_encrypted=encrypted_access_token,
                ml_refresh_token_encrypted=encrypted_refresh_token,
                ml_token_type="bearer",  # nosec B106
                ml_expires_at=expires_at,
                ml_refresh_expires_at=refresh_expires_at,
                ml_scopes="offline_access read write",
                ml_user_id=ml_user_id,
                ml_nickname=user_info.get("nickname"),
                ml_email=user_info.get("email"),
                ml_site_id=site_id,
                ml_auth_domain=self._ml_client.get_auth_domain(site_id),
                ml_is_valid=True,
                created_at=datetime.now(UTC),
            )

            # Save credentials
            await self._credentials_repository.save(credentials)

            return credentials

        except MLOAuthError as e:
            raise AuthenticationError(f"OAuth authentication failed: {e}") from e
        except MLRateLimitError as e:
            raise AuthenticationError(f"OAuth authentication failed: {e}") from e
        except MLManagerAccountError as e:
            raise AuthenticationError(str(e)) from e
        except Exception as e:
            raise AuthenticationError(f"Failed to complete OAuth flow: {e}") from e

    async def refresh_token(self, credentials: MLCredentials) -> MLCredentials:
        """Refresh access token using refresh token."""
        try:
            # Decrypt refresh token
            refresh_token = self._encryption_service.decrypt_refresh_token(
                credentials.ml_refresh_token_encrypted
            )

            # Refresh tokens
            token_response = await self._ml_client.refresh_tokens(refresh_token)

            access_token = token_response["access_token"]
            new_refresh_token = token_response["refresh_token"]
            expires_in = token_response["expires_in"]

            # Calculate new expiration times
            expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
            refresh_expires_at = datetime.now(UTC) + timedelta(days=180)

            # Encrypt new tokens
            encrypted_access_token = self._encryption_service.encrypt_access_token(
                access_token
            )
            encrypted_refresh_token = self._encryption_service.encrypt_refresh_token(
                new_refresh_token
            )

            # Update credentials with new tokens
            credentials.update_tokens(
                access_token_encrypted=encrypted_access_token,
                refresh_token_encrypted=encrypted_refresh_token,
                expires_at=expires_at,
                refresh_expires_at=refresh_expires_at,
            )

            # Save updated credentials
            await self._credentials_repository.save(credentials)

            return credentials

        except Exception as e:
            credentials.mark_invalid(f"Token refresh failed: {e}")
            await self._credentials_repository.save(credentials)
            raise AuthenticationError(f"Failed to refresh token: {e}") from e

    async def validate_connection(self, credentials: MLCredentials) -> ConnectionStatus:
        """Validate connection health and token validity."""
        try:
            # Check if tokens are expired
            if credentials.is_refresh_token_expired:
                return ConnectionStatus(
                    is_connected=False,
                    connection_health="expired",
                    error_message="Refresh token expired, reconnection required",
                )

            # Try to validate access token
            access_token = self._encryption_service.decrypt_access_token(
                credentials.ml_access_token_encrypted
            )

            is_valid = await self._ml_client.validate_token(access_token)

            if is_valid:
                credentials.mark_valid()
                await self._credentials_repository.save(credentials)

                return ConnectionStatus(
                    is_connected=True,
                    connection_health="healthy",
                    ml_nickname=credentials.ml_nickname,
                    ml_email=credentials.ml_email,
                    ml_site_id=credentials.ml_site_id,
                    expires_at=credentials.ml_expires_at,
                    last_validated_at=credentials.ml_last_validated_at,
                )
            else:
                # Try to refresh if access token is invalid but refresh token is valid
                if not credentials.is_refresh_token_expired:
                    try:
                        refreshed_credentials = await self.refresh_token(credentials)
                        return ConnectionStatus(
                            is_connected=True,
                            connection_health="healthy",
                            ml_nickname=refreshed_credentials.ml_nickname,
                            ml_email=refreshed_credentials.ml_email,
                            ml_site_id=refreshed_credentials.ml_site_id,
                            expires_at=refreshed_credentials.ml_expires_at,
                            last_validated_at=refreshed_credentials.ml_last_validated_at,
                        )
                    except Exception:  # nosec B110
                        # Silently ignore token refresh failures, will mark as invalid below
                        pass

                credentials.mark_invalid("Token validation failed")
                await self._credentials_repository.save(credentials)

                return ConnectionStatus(
                    is_connected=False,
                    connection_health="invalid",
                    error_message="Token validation failed",
                )

        except Exception as e:
            credentials.mark_invalid(f"Connection validation failed: {e}")
            await self._credentials_repository.save(credentials)

            return ConnectionStatus(
                is_connected=False,
                connection_health="invalid",
                error_message=str(e),
            )

    async def disconnect(self, user_id: UUID) -> bool:
        """Disconnect MercadoLibre integration for user."""
        try:
            return await self._credentials_repository.delete_by_user_id(user_id)
        except Exception:
            return False

    async def get_connection_status(self, user_id: UUID) -> ConnectionStatus:
        """Get connection status for user."""
        credentials = await self._credentials_repository.find_by_user_id(user_id)

        if not credentials:
            return ConnectionStatus(
                is_connected=False,
                connection_health="disconnected",
            )

        return await self.validate_connection(credentials)

    async def schedule_token_refresh(self, credentials: MLCredentials) -> bool:
        """Schedule automatic token refresh at 5.5 hours."""
        # In a real implementation, this would schedule a background task
        # For now, we'll check if refresh is needed
        return credentials.should_refresh_token

    async def process_expired_tokens(self) -> int:
        """Process and refresh expired tokens."""
        # Find tokens that should be refreshed (at 5.5 hours)
        refresh_threshold = datetime.now(UTC) + timedelta(
            minutes=30
        )  # 30 minutes from now

        try:
            expiring_credentials = (
                await self._credentials_repository.find_expiring_tokens(
                    refresh_threshold
                )
            )

            processed_count = 0
            for credentials in expiring_credentials:
                if (
                    credentials.should_refresh_token
                    and not credentials.is_refresh_token_expired
                ):
                    try:
                        await self.refresh_token(credentials)
                        processed_count += 1
                    except Exception:
                        # Mark as invalid if refresh fails
                        credentials.mark_invalid("Automatic refresh failed")
                        await self._credentials_repository.save(credentials)

            return processed_count

        except Exception:
            return 0

    async def validate_manager_account(self, access_token: str) -> bool:
        """Validate that the account is a manager account."""
        return await self._ml_client.check_manager_account(access_token)

    async def generate_pkce_parameters(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge."""
        # Generate code verifier (43-128 characters, base64url encoded)
        code_verifier = (
            base64.urlsafe_b64encode(secrets.token_bytes(96))
            .decode("utf-8")
            .rstrip("=")
        )

        # Generate code challenge (SHA256 of verifier)
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )

        return code_verifier, code_challenge

    async def validate_state_parameter(self, state: str, user_id: UUID) -> bool:
        """Validate CSRF state parameter."""
        state_data = self._state_storage.get(state)
        if not state_data:
            return False

        # Check if state belongs to the user
        if state_data["user_id"] != str(user_id):
            return False

        # Check if state is not too old (5 minutes max)
        created_at = state_data["created_at"]
        if datetime.now(UTC) - created_at > timedelta(minutes=5):
            # Clean up expired state
            del self._state_storage[state]
            return False

        return True

    async def get_user_credentials(self, user_id: UUID) -> MLCredentials | None:
        """Get ML credentials for user."""
        return await self._credentials_repository.find_by_user_id(user_id)

    async def update_user_info(
        self, credentials: MLCredentials, access_token: str
    ) -> MLCredentials:
        """Update user information from MercadoLibre API."""
        try:
            user_info = await self._ml_client.get_user_info(access_token)

            credentials.update_user_info(
                ml_user_id=user_info["id"],
                nickname=user_info.get("nickname"),
                email=user_info.get("email"),
            )

            await self._credentials_repository.save(credentials)
            return credentials

        except Exception as e:
            raise AuthenticationError(f"Failed to update user info: {e}") from e
