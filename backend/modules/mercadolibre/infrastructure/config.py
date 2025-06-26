"""
MercadoLibre module configuration.

This module provides configuration specific to MercadoLibre integration,
including API settings, rate limiting, and marketplace-specific configurations.
"""

from typing import Any

from pydantic import Field

from infrastructure.config.base_config import BaseModuleConfig, ExternalServiceMixin


class MercadoLibreModuleConfig(BaseModuleConfig, ExternalServiceMixin):
    """
    Configuration for the MercadoLibre integration module.

    This configuration includes API credentials, rate limiting,
    marketplace-specific settings, and integration parameters.
    """

    module_name: str = Field(
        default="mercadolibre", description="MercadoLibre module identifier"
    )

    # API configuration
    client_id: str | None = Field(
        default=None, description="MercadoLibre API client ID"
    )
    client_secret: str | None = Field(
        default=None, description="MercadoLibre API client secret"
    )
    api_base_url: str = Field(
        default="https://api.mercadolibre.com", description="MercadoLibre API base URL"
    )
    auth_url: str = Field(
        default="https://auth.mercadolibre.com.ar/authorization",
        description="MercadoLibre authorization URL",
    )

    # Rate limiting configuration
    requests_per_minute: int = Field(
        default=200, description="Maximum requests per minute"
    )
    requests_per_hour: int = Field(
        default=1000, description="Maximum requests per hour"
    )
    burst_limit: int = Field(default=10, description="Burst request limit")

    # Token management
    access_token_expire_minutes: int = Field(
        default=120, description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=180, description="Refresh token expiration in days"
    )
    token_refresh_buffer_minutes: int = Field(
        default=10, description="Token refresh buffer in minutes"
    )

    # Marketplace configuration
    default_country: str = Field(
        default="AR", description="Default country code for MercadoLibre"
    )
    default_currency: str = Field(default="ARS", description="Default currency")
    supported_countries: list[str] = Field(
        default=["AR", "BR", "MX", "CO", "CL", "PE", "UY"],
        description="Supported MercadoLibre countries",
    )

    # Publication settings
    max_photos_per_listing: int = Field(
        default=12, description="Maximum photos per listing"
    )
    photo_min_width: int = Field(
        default=500, description="Minimum photo width in pixels"
    )
    photo_min_height: int = Field(
        default=500, description="Minimum photo height in pixels"
    )
    photo_max_size_mb: int = Field(default=10, description="Maximum photo size in MB")

    # Sync configuration
    sync_interval_minutes: int = Field(
        default=15, description="Sync interval in minutes"
    )
    batch_size: int = Field(default=50, description="Batch size for bulk operations")
    max_concurrent_requests: int = Field(
        default=5, description="Maximum concurrent API requests"
    )

    # Error handling
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    retry_delay_seconds: int = Field(
        default=1, description="Delay between retries in seconds"
    )
    backoff_multiplier: float = Field(
        default=2.0, description="Exponential backoff multiplier"
    )

    # Webhook configuration
    webhook_secret: str | None = Field(
        default=None, description="Webhook secret for validation"
    )
    webhook_timeout_seconds: int = Field(
        default=30, description="Webhook processing timeout"
    )

    class Config(BaseModuleConfig.Config):
        """Pydantic configuration for MercadoLibre module."""

        env_prefix = "INTELLIPOST_MERCADOLIBRE_"

    def get_module_specific_settings(self) -> dict[str, Any]:
        """Get MercadoLibre module specific settings."""
        return {
            "api": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "base_url": self.api_base_url,
                "auth_url": self.auth_url,
            },
            "rate_limiting": {
                "requests_per_minute": self.requests_per_minute,
                "requests_per_hour": self.requests_per_hour,
                "burst_limit": self.burst_limit,
            },
            "tokens": {
                "access_token_expire_minutes": self.access_token_expire_minutes,
                "refresh_token_expire_days": self.refresh_token_expire_days,
                "refresh_buffer_minutes": self.token_refresh_buffer_minutes,
            },
            "marketplace": {
                "default_country": self.default_country,
                "default_currency": self.default_currency,
                "supported_countries": self.supported_countries,
            },
            "publication": {
                "max_photos_per_listing": self.max_photos_per_listing,
                "photo_min_width": self.photo_min_width,
                "photo_min_height": self.photo_min_height,
                "photo_max_size_mb": self.photo_max_size_mb,
            },
            "sync": {
                "interval_minutes": self.sync_interval_minutes,
                "batch_size": self.batch_size,
                "max_concurrent_requests": self.max_concurrent_requests,
            },
            "error_handling": {
                "max_retries": self.max_retries,
                "retry_delay_seconds": self.retry_delay_seconds,
                "backoff_multiplier": self.backoff_multiplier,
            },
            "webhooks": {
                "secret": self.webhook_secret,
                "timeout_seconds": self.webhook_timeout_seconds,
            },
        }


# Global MercadoLibre module configuration instance
mercadolibre_config = MercadoLibreModuleConfig()
