"""
Unit tests for MercadoLibre OAuth service.

Tests the OAuth service implementation including PKCE flow,
token refresh, and manager account validation.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from modules.user_management.domain.entities.ml_credentials import MLCredentials
from modules.user_management.domain.exceptions import (
    AuthenticationError,
    ValidationError,
)
from modules.user_management.infrastructure.services.mercadolibre_api_client import (
    MLManagerAccountError,
    MLOAuthError,
    MLRateLimitError,
)
from modules.user_management.infrastructure.services.ml_oauth_service import (
    MLOAuthService,
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestMLOAuthService:
    """Test suite for ML OAuth service."""

    @pytest.fixture
    def mock_ml_client(self):
        """Mock MercadoLibre API client."""
        mock = AsyncMock()

        # Override sync methods with regular MagicMock
        mock.build_auth_url = MagicMock(
            return_value="https://auth.mercadolibre.com.ar/authorization?..."
        )
        mock.get_site_domain = MagicMock(return_value="mercadolibre.com.ar")
        mock.get_auth_domain = MagicMock(return_value="mercadolibre.com.ar")

        return mock

    @pytest.fixture
    def mock_credentials_repository(self):
        """Mock credentials repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_encryption_service(self):
        """Mock encryption service."""
        mock = MagicMock()
        mock.encrypt_access_token.return_value = "encrypted_access_token"
        mock.encrypt_refresh_token.return_value = "encrypted_refresh_token"
        mock.encrypt_app_secret.return_value = "encrypted_app_secret"
        mock.decrypt_access_token.return_value = "decrypted_access_token"
        mock.decrypt_refresh_token.return_value = "decrypted_refresh_token"
        return mock

    @pytest.fixture
    def oauth_service(
        self, mock_ml_client, mock_credentials_repository, mock_encryption_service
    ):
        """Create OAuth service with mocked dependencies."""
        return MLOAuthService(
            ml_client=mock_ml_client,
            credentials_repository=mock_credentials_repository,
            encryption_service=mock_encryption_service,
            app_id="test_app_id",
            app_secret="test_app_secret",
        )

    @pytest.fixture
    def sample_credentials(self):
        """Create sample ML credentials."""
        return MLCredentials(
            id=uuid4(),
            user_id=uuid4(),
            ml_app_id="test_app_id",
            ml_secret_key_encrypted="encrypted_secret",
            ml_access_token_encrypted="encrypted_access_token",
            ml_refresh_token_encrypted="encrypted_refresh_token",
            ml_token_type="bearer",
            ml_expires_at=datetime.now(UTC) + timedelta(hours=6),
            ml_refresh_expires_at=datetime.now(UTC) + timedelta(days=180),
            ml_scopes="offline_access read write",
            ml_user_id=12345,
            ml_nickname="test_user",
            ml_email="test@example.com",
            ml_site_id="MLA",
            ml_auth_domain="auth.mercadolibre.com.ar",
            ml_is_valid=True,
            created_at=datetime.now(UTC),
        )

    # Test OAuth flow initiation
    async def test_initiate_oauth_flow_success(self, oauth_service, mock_ml_client):
        """Test successful OAuth flow initiation."""
        user_id = uuid4()
        redirect_uri = "https://example.com/callback"
        site_id = "MLA"

        # Mock ML client response
        mock_ml_client.build_auth_url.return_value = (
            "https://auth.mercadolibre.com.ar/authorization?..."
        )

        # Execute
        result = await oauth_service.initiate_oauth_flow(user_id, redirect_uri, site_id)

        # Assertions
        assert (
            result.authorization_url
            == "https://auth.mercadolibre.com.ar/authorization?..."
        )
        assert result.state is not None
        assert result.code_verifier is not None
        assert result.code_challenge is not None
        assert result.site_id == site_id
        assert result.redirect_uri == redirect_uri

        # Verify ML client was called correctly
        mock_ml_client.build_auth_url.assert_called_once()

    async def test_initiate_oauth_flow_invalid_site_id(self, oauth_service):
        """Test OAuth initiation with invalid site ID."""
        user_id = uuid4()
        redirect_uri = "https://example.com/callback"
        invalid_site_id = "INVALID"

        with pytest.raises(ValidationError, match="Invalid site_id"):
            await oauth_service.initiate_oauth_flow(
                user_id, redirect_uri, invalid_site_id
            )

    async def test_initiate_oauth_flow_invalid_redirect_uri(self, oauth_service):
        """Test OAuth initiation with invalid redirect URI."""
        user_id = uuid4()
        invalid_redirect_uri = "not-a-url"

        with pytest.raises(ValidationError, match="Invalid redirect_uri"):
            await oauth_service.initiate_oauth_flow(user_id, invalid_redirect_uri)

    # Test OAuth callback handling
    async def test_handle_oauth_callback_success(
        self,
        oauth_service,
        mock_ml_client,
        mock_credentials_repository,
        sample_credentials,
    ):
        """Test successful OAuth callback handling."""
        user_id = uuid4()
        code = "auth_code_123"
        state = "state_123"
        code_verifier = "code_verifier_123"

        # Setup state storage
        oauth_service._state_storage[state] = {
            "user_id": str(user_id),
            "code_verifier": code_verifier,
            "site_id": "MLA",
            "redirect_uri": "https://example.com/callback",
            "created_at": datetime.now(UTC),
        }

        # Mock ML client responses
        mock_ml_client.exchange_code_for_tokens.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "expires_in": 21600,  # 6 hours
            "user_id": 12345,
        }
        mock_ml_client.get_user_info.return_value = {
            "id": 12345,
            "nickname": "test_user",
            "email": "test@example.com",
        }

        # Execute
        result = await oauth_service.handle_oauth_callback(
            user_id, code, state, code_verifier
        )

        # Assertions
        assert result.ml_user_id == 12345
        assert result.ml_nickname == "test_user"
        assert result.ml_email == "test@example.com"
        assert result.ml_site_id == "MLA"
        assert result.ml_is_valid is True

        # Verify repository save was called
        mock_credentials_repository.save.assert_called_once()

    async def test_handle_oauth_callback_manager_account_error(
        self, oauth_service, mock_ml_client
    ):
        """Test OAuth callback with manager account validation failure."""
        user_id = uuid4()
        code = "auth_code_123"
        state = "state_123"
        code_verifier = "code_verifier_123"

        # Setup state storage
        oauth_service._state_storage[state] = {
            "user_id": str(user_id),
            "code_verifier": code_verifier,
            "site_id": "MLA",
            "redirect_uri": "https://example.com/callback",
            "created_at": datetime.now(UTC),
        }

        # Mock ML client to raise manager account error
        mock_ml_client.exchange_code_for_tokens.side_effect = MLManagerAccountError(
            "Only manager accounts can authorize applications",
            "Please use a manager account",
        )

        with pytest.raises(
            AuthenticationError,
            match="Only manager accounts can authorize applications",
        ):
            await oauth_service.handle_oauth_callback(
                user_id, code, state, code_verifier
            )

    async def test_handle_oauth_callback_invalid_state(self, oauth_service):
        """Test OAuth callback with invalid state parameter."""
        user_id = uuid4()
        code = "auth_code_123"
        invalid_state = "invalid_state"
        code_verifier = "code_verifier_123"

        with pytest.raises(ValidationError, match="Invalid state parameter"):
            await oauth_service.handle_oauth_callback(
                user_id, code, invalid_state, code_verifier
            )

    # Test token refresh
    async def test_refresh_token_success(
        self,
        oauth_service,
        mock_ml_client,
        mock_credentials_repository,
        sample_credentials,
    ):
        """Test successful token refresh."""
        # Mock ML client response
        mock_ml_client.refresh_tokens.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 21600,
        }

        # Execute
        result = await oauth_service.refresh_token(sample_credentials)

        # Assertions
        assert result.ml_is_valid is True
        assert result.ml_validation_error is None

        # Verify repository save was called
        mock_credentials_repository.save.assert_called_once()

    async def test_refresh_token_failure(
        self,
        oauth_service,
        mock_ml_client,
        mock_credentials_repository,
        sample_credentials,
    ):
        """Test token refresh failure."""
        # Mock ML client to raise error
        mock_ml_client.refresh_tokens.side_effect = MLOAuthError(
            "Token refresh failed", "invalid_grant", 400
        )

        with pytest.raises(AuthenticationError, match="Failed to refresh token"):
            await oauth_service.refresh_token(sample_credentials)

        # Verify credential was marked as invalid
        mock_credentials_repository.save.assert_called_once()

    # Test connection validation
    async def test_validate_connection_healthy(
        self,
        oauth_service,
        mock_ml_client,
        mock_credentials_repository,
        sample_credentials,
    ):
        """Test connection validation for healthy connection."""
        # Mock ML client to return valid token
        mock_ml_client.validate_token.return_value = True

        # Execute
        result = await oauth_service.validate_connection(sample_credentials)

        # Assertions
        assert result.is_connected is True
        assert result.connection_health == "healthy"
        assert result.ml_nickname == "test_user"
        assert result.ml_email == "test@example.com"

    async def test_validate_connection_expired_refresh_token(
        self, oauth_service, sample_credentials
    ):
        """Test connection validation with expired refresh token."""
        # Set refresh token as expired
        sample_credentials.ml_refresh_expires_at = datetime.now(UTC) - timedelta(days=1)

        # Execute
        result = await oauth_service.validate_connection(sample_credentials)

        # Assertions
        assert result.is_connected is False
        assert result.connection_health == "expired"
        assert "Refresh token expired" in result.error_message

    async def test_validate_connection_invalid_token_with_refresh(
        self,
        oauth_service,
        mock_ml_client,
        mock_credentials_repository,
        sample_credentials,
    ):
        """Test connection validation with invalid token but valid refresh."""
        # Mock ML client responses
        mock_ml_client.validate_token.return_value = False
        mock_ml_client.refresh_tokens.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 21600,
        }

        # Execute
        result = await oauth_service.validate_connection(sample_credentials)

        # Assertions
        assert result.is_connected is True
        assert result.connection_health == "healthy"

        # Verify token refresh was attempted
        mock_ml_client.refresh_tokens.assert_called_once()

    # Test PKCE parameters generation
    async def test_generate_pkce_parameters(self, oauth_service):
        """Test PKCE parameters generation."""
        code_verifier, code_challenge = await oauth_service.generate_pkce_parameters()

        # Assertions
        assert len(code_verifier) == 128  # Should be 128 characters as per story spec
        assert len(code_challenge) == 43  # SHA256 base64url encoded is 43 chars
        assert code_verifier != code_challenge

        # Verify code challenge is SHA256 of verifier
        import base64
        import hashlib

        expected_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )
        assert code_challenge == expected_challenge

    # Test state parameter validation
    async def test_validate_state_parameter_valid(self, oauth_service):
        """Test state parameter validation with valid state."""
        user_id = uuid4()
        state = "test_state"

        # Add state to storage
        oauth_service._state_storage[state] = {
            "user_id": str(user_id),
            "code_verifier": "test_verifier",
            "site_id": "MLA",
            "redirect_uri": "https://example.com/callback",
            "created_at": datetime.now(UTC),
        }

        # Execute
        result = await oauth_service.validate_state_parameter(state, user_id)

        # Assertions
        assert result is True

    async def test_validate_state_parameter_expired(self, oauth_service):
        """Test state parameter validation with expired state."""
        user_id = uuid4()
        state = "test_state"

        # Add expired state to storage
        oauth_service._state_storage[state] = {
            "user_id": str(user_id),
            "code_verifier": "test_verifier",
            "site_id": "MLA",
            "redirect_uri": "https://example.com/callback",
            "created_at": datetime.now(UTC) - timedelta(minutes=10),  # Expired
        }

        # Execute
        result = await oauth_service.validate_state_parameter(state, user_id)

        # Assertions
        assert result is False
        assert state not in oauth_service._state_storage  # Should be cleaned up

    async def test_validate_state_parameter_wrong_user(self, oauth_service):
        """Test state parameter validation with wrong user ID."""
        user_id = uuid4()
        wrong_user_id = uuid4()
        state = "test_state"

        # Add state for different user
        oauth_service._state_storage[state] = {
            "user_id": str(wrong_user_id),
            "code_verifier": "test_verifier",
            "site_id": "MLA",
            "redirect_uri": "https://example.com/callback",
            "created_at": datetime.now(UTC),
        }

        # Execute
        result = await oauth_service.validate_state_parameter(state, user_id)

        # Assertions
        assert result is False

    # Test manager account validation
    async def test_validate_manager_account_success(
        self, oauth_service, mock_ml_client
    ):
        """Test manager account validation success."""
        access_token = "test_token"
        mock_ml_client.check_manager_account.return_value = True

        result = await oauth_service.validate_manager_account(access_token)

        assert result is True
        mock_ml_client.check_manager_account.assert_called_once_with(access_token)

    async def test_validate_manager_account_failure(
        self, oauth_service, mock_ml_client
    ):
        """Test manager account validation failure."""
        access_token = "test_token"
        mock_ml_client.check_manager_account.return_value = False

        result = await oauth_service.validate_manager_account(access_token)

        assert result is False

    # Test disconnect functionality
    async def test_disconnect_success(self, oauth_service, mock_credentials_repository):
        """Test successful disconnect."""
        user_id = uuid4()
        mock_credentials_repository.delete_by_user_id.return_value = True

        result = await oauth_service.disconnect(user_id)

        assert result is True
        mock_credentials_repository.delete_by_user_id.assert_called_once_with(user_id)

    async def test_disconnect_not_connected(
        self, oauth_service, mock_credentials_repository
    ):
        """Test disconnect when user is not connected."""
        user_id = uuid4()
        mock_credentials_repository.delete_by_user_id.return_value = False

        result = await oauth_service.disconnect(user_id)

        assert result is False

    # Test process expired tokens
    async def test_process_expired_tokens(
        self,
        oauth_service,
        mock_credentials_repository,
        mock_ml_client,
        sample_credentials,
    ):
        """Test processing of expired tokens."""
        # Make the credentials expire in 20 minutes (should be refreshed)
        sample_credentials.ml_expires_at = datetime.now(UTC) + timedelta(minutes=20)

        # Mock repository to return expiring credentials
        expiring_credentials = [sample_credentials]
        mock_credentials_repository.find_expiring_tokens.return_value = (
            expiring_credentials
        )

        # Mock successful token refresh
        mock_ml_client.refresh_tokens.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 21600,
        }

        # Execute
        result = await oauth_service.process_expired_tokens()

        # Assertions
        assert result == 1  # One token processed

    # Test rate limiting handling
    async def test_handle_rate_limit_error(self, oauth_service, mock_ml_client):
        """Test handling of rate limit errors."""
        user_id = uuid4()
        code = "auth_code_123"
        state = "state_123"
        code_verifier = "code_verifier_123"

        # Setup state storage
        oauth_service._state_storage[state] = {
            "user_id": str(user_id),
            "code_verifier": code_verifier,
            "site_id": "MLA",
            "redirect_uri": "https://example.com/callback",
            "created_at": datetime.now(UTC),
        }

        # Mock ML client to raise rate limit error
        mock_ml_client.exchange_code_for_tokens.side_effect = MLRateLimitError(
            "Rate limit exceeded", 60
        )

        with pytest.raises(AuthenticationError, match="OAuth authentication failed"):
            await oauth_service.handle_oauth_callback(
                user_id, code, state, code_verifier
            )

    # Test edge cases
    async def test_get_connection_status_not_connected(
        self, oauth_service, mock_credentials_repository
    ):
        """Test getting connection status when user is not connected."""
        user_id = uuid4()
        mock_credentials_repository.find_by_user_id.return_value = None

        result = await oauth_service.get_connection_status(user_id)

        assert result.is_connected is False
        assert result.connection_health == "disconnected"

    async def test_update_user_info_success(
        self,
        oauth_service,
        mock_ml_client,
        mock_credentials_repository,
        sample_credentials,
    ):
        """Test updating user info from ML API."""
        access_token = "test_token"
        mock_ml_client.get_user_info.return_value = {
            "id": 54321,
            "nickname": "updated_user",
            "email": "updated@example.com",
        }

        result = await oauth_service.update_user_info(sample_credentials, access_token)

        assert result.ml_user_id == 54321
        assert result.ml_nickname == "updated_user"
        assert result.ml_email == "updated@example.com"
        mock_credentials_repository.save.assert_called_once()

    async def test_update_user_info_failure(
        self, oauth_service, mock_ml_client, sample_credentials
    ):
        """Test updating user info failure."""
        access_token = "test_token"
        mock_ml_client.get_user_info.side_effect = Exception("API error")

        with pytest.raises(AuthenticationError, match="Failed to update user info"):
            await oauth_service.update_user_info(sample_credentials, access_token)
