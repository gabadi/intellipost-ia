"""
Configuration API router.

This module provides endpoints for retrieving application configuration
that affects frontend behavior.
"""

from fastapi import APIRouter

from api.schemas.config import ConfigValidationResponse, FeatureFlagsResponse
from infrastructure.config.settings import Settings

router = APIRouter(prefix="/config", tags=["configuration"])


def create_config_router(settings: Settings) -> APIRouter:
    """Create configuration router with dependency injection."""

    @router.get("/features")
    async def get_feature_flags() -> FeatureFlagsResponse:  # pyright: ignore[reportUnusedFunction]
        """Get feature flags for frontend configuration."""
        return FeatureFlagsResponse(
            registration_enabled=settings.user_registration_enabled,
        )

    @router.get("/validation")
    async def get_config_validation() -> ConfigValidationResponse:  # pyright: ignore[reportUnusedFunction]
        """Get configuration validation status for production readiness."""
        validations = settings.validate_configuration()
        return ConfigValidationResponse(
            environment=settings.environment,
            is_production_ready=all(validations.values()),
            validations=validations,
            warnings=_get_config_warnings(settings),
        )

    def _get_config_warnings(settings: Settings) -> list[str]:
        """Get configuration warnings for production deployment."""
        warnings: list[str] = []

        if settings.is_production:
            if not settings.ml_app_id:
                warnings.append("MercadoLibre app ID not configured")
            if not settings.ml_app_secret:
                warnings.append("MercadoLibre app secret not configured")
            if not settings.ml_encryption_key:
                warnings.append("MercadoLibre encryption key not configured")
            if settings.debug:
                warnings.append("Debug mode enabled in production")

        return warnings

    return router
