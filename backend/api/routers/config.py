"""
Configuration API router.

This module provides endpoints for retrieving application configuration
that affects frontend behavior.
"""

from fastapi import APIRouter

from infrastructure.config.settings import Settings

router = APIRouter(prefix="/config", tags=["configuration"])


def create_config_router(settings: Settings) -> APIRouter:
    """Create configuration router with dependency injection."""

    @router.get("/features")
    async def get_feature_flags() -> dict[str, bool]:
        """Get feature flags for frontend configuration."""
        return {
            "registration_enabled": settings.user_registration_enabled,
        }

    return router
