"""
MercadoLibre Credentials domain entity for user management module.

This module contains the ML credentials entity for storing and managing
MercadoLibre OAuth 2.0 authentication credentials and related data.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class MLCredentials:
    """
    MercadoLibre Credentials domain entity for OAuth 2.0 integration.

    This entity manages all MercadoLibre OAuth 2.0 credentials, tokens,
    and related metadata following the story specifications for Epic 6 Story 2.
    """

    # Core identity (required fields)
    id: UUID
    user_id: UUID

    # MercadoLibre app credentials (required fields)
    ml_app_id: str
    ml_secret_key_encrypted: str

    # OAuth tokens (required fields)
    ml_access_token_encrypted: str
    ml_refresh_token_encrypted: str
    ml_expires_at: datetime
    ml_refresh_expires_at: datetime

    # MercadoLibre user information (required fields)
    ml_user_id: int

    # Timestamps (required fields)
    created_at: datetime

    # OAuth tokens (fields with defaults)
    ml_token_type: str = "bearer"

    # OAuth scopes and permissions (fields with defaults)
    ml_scopes: str = "offline_access read write"

    # MercadoLibre user information (fields with defaults)
    ml_nickname: str | None = None
    ml_email: str | None = None

    # Country-specific data (ENHANCED per story, fields with defaults)
    ml_site_id: str = "MLA"  # MLA/MLM/MBL/MLC/MCO support
    ml_auth_domain: str | None = None  # Country-specific auth domain used

    # Connection health and validation (fields with defaults)
    ml_is_valid: bool = False
    ml_last_validated_at: datetime | None = None
    ml_validation_error: str | None = None

    # PKCE temporary storage during OAuth flow (ENHANCED per story, fields with defaults)
    pkce_code_challenge: str | None = None  # Temporary storage
    pkce_code_verifier: str | None = None  # Temporary storage

    # Timestamps (fields with defaults)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        # Validate site_id
        valid_sites = {"MLA", "MLM", "MBL", "MLC", "MCO"}
        if self.ml_site_id not in valid_sites:
            raise ValueError(
                f"Invalid site_id: {self.ml_site_id}. Must be one of: {valid_sites}"
            )

        # Validate scopes
        required_scopes = {"offline_access", "read", "write"}
        current_scopes = set(self.ml_scopes.split())
        if not required_scopes.issubset(current_scopes):
            raise ValueError(
                f"Missing required scopes. Required: {required_scopes}, Current: {current_scopes}"
            )

    @property
    def is_token_expired(self) -> bool:
        """Check if access token is expired."""
        return datetime.now(UTC) >= self.ml_expires_at

    @property
    def is_refresh_token_expired(self) -> bool:
        """Check if refresh token is expired."""
        return datetime.now(UTC) >= self.ml_refresh_expires_at

    @property
    def should_refresh_token(self) -> bool:
        """Check if token should be refreshed (at 5.5 hours before 6-hour expiry)."""
        refresh_threshold = self.ml_expires_at.timestamp() - (
            5.5 * 3600
        )  # 5.5 hours before expiry
        return datetime.now(UTC).timestamp() >= refresh_threshold

    @property
    def connection_health(self) -> str:
        """Get connection health status."""
        if not self.ml_is_valid:
            return "invalid"
        elif self.is_refresh_token_expired or self.is_token_expired:
            return "expired"
        else:
            return "healthy"

    def update_tokens(
        self,
        access_token_encrypted: str,
        refresh_token_encrypted: str,
        expires_at: datetime,
        refresh_expires_at: datetime,
    ) -> None:
        """
        Update OAuth tokens with new values.

        CRITICAL: Implements single-use refresh token requirement.
        Each token refresh must generate new access + refresh tokens.
        """
        self.ml_access_token_encrypted = access_token_encrypted
        self.ml_refresh_token_encrypted = refresh_token_encrypted
        self.ml_expires_at = expires_at
        self.ml_refresh_expires_at = refresh_expires_at
        self.ml_is_valid = True
        self.ml_validation_error = None
        self.updated_at = datetime.now(UTC)

    def update_user_info(
        self, ml_user_id: int, nickname: str | None = None, email: str | None = None
    ) -> None:
        """Update MercadoLibre user information."""
        self.ml_user_id = ml_user_id
        self.ml_nickname = nickname
        self.ml_email = email
        self.updated_at = datetime.now(UTC)

    def set_pkce_parameters(self, code_challenge: str, code_verifier: str) -> None:
        """
        Set PKCE parameters for OAuth flow.

        CRITICAL: Implements PKCE security requirement (SHA-256 method).
        Used for temporary storage during OAuth authorization flow.
        """
        self.pkce_code_challenge = code_challenge
        self.pkce_code_verifier = code_verifier
        self.updated_at = datetime.now(UTC)

    def clear_pkce_parameters(self) -> None:
        """Clear PKCE parameters after OAuth flow completion."""
        self.pkce_code_challenge = None
        self.pkce_code_verifier = None
        self.updated_at = datetime.now(UTC)

    def mark_invalid(self, error: str) -> None:
        """Mark credentials as invalid with error message."""
        self.ml_is_valid = False
        self.ml_validation_error = error
        self.ml_last_validated_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def mark_valid(self) -> None:
        """Mark credentials as valid and clear error."""
        self.ml_is_valid = True
        self.ml_validation_error = None
        self.ml_last_validated_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def get_auth_domain(self) -> str:
        """Get authentication domain for site_id."""
        domain_mapping = {
            "MLA": "auth.mercadolibre.com.ar",
            "MLM": "auth.mercadolibre.com.mx",
            "MBL": "auth.mercadolibre.com.br",
            "MLC": "auth.mercadolibre.cl",
            "MCO": "auth.mercadolibre.com.co",
        }
        return domain_mapping.get(self.ml_site_id, "auth.mercadolibre.com.ar")

    def get_token_endpoint(self) -> str:
        """Get OAuth token endpoint URL."""
        return "https://api.mercadolibre.com/oauth/token"

    def is_manager_account_required(self) -> bool:
        """
        Check if manager account is required.

        CRITICAL: Only manager accounts can authorize applications.
        Collaborator accounts must be rejected.
        """
        return True  # Always true for MercadoLibre OAuth

    def time_until_refresh(self) -> int:
        """Get seconds until token refresh should occur."""
        if self.should_refresh_token:
            return 0
        refresh_threshold = self.ml_expires_at.timestamp() - (5.5 * 3600)
        return max(0, int(refresh_threshold - datetime.now(UTC).timestamp()))

    def __str__(self) -> str:
        """String representation of ML credentials."""
        return f"MLCredentials(user_id={self.user_id}, site_id={self.ml_site_id}, health={self.connection_health})"

    def __repr__(self) -> str:
        """Detailed representation of ML credentials."""
        return (
            f"MLCredentials(id={self.id}, user_id={self.user_id}, "
            f"site_id={self.ml_site_id}, ml_user_id={self.ml_user_id}, "
            f"expires_at={self.ml_expires_at}, health={self.connection_health})"
        )
