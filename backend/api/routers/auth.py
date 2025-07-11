"""
Authentication router wrapper to avoid circular imports.

This module provides a clean interface for creating the auth router
without creating circular dependencies with the DI container.
"""

from fastapi import APIRouter

from api.dependencies import create_auth_router_factory


def create_auth_router_with_dependencies(
    access_token_expire_minutes: int = 15,
    registration_enabled: bool = False,
) -> APIRouter:
    """Create auth router with dependency injection factories."""
    return create_auth_router_factory(
        access_token_expire_minutes=access_token_expire_minutes,
        registration_enabled=registration_enabled,
    )
