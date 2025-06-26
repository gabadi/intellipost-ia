"""
Dependency injection configuration for FastAPI.

This module provides dependency injection setup for the hexagonal architecture,
ensuring loose coupling between layers through Protocol-based interfaces.
"""

from typing import Annotated, Any

from fastapi import Depends

from .logging import get_logger
from .settings import Settings


# Settings dependency
def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Logger dependency
def get_app_logger(name: str = "main"):
    """Get application logger instance."""
    return get_logger(name)


# Type aliases for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
LoggerDep = Annotated[
    Any, Depends(get_app_logger)
]  # Will be properly typed when logger interface is defined


# Repository protocol dependencies (to be implemented by infrastructure layer)
class DependencyContainer:
    """
    Container for managing service dependencies in hexagonal architecture.

    This approach provides several benefits over pure FastAPI Depends():
    1. Explicit dependency registration during application startup with fail-fast validation
    2. Protocol-based contracts ensuring proper hexagonal architecture boundaries
    3. Centralized dependency management for better testing and mocking
    4. Clear separation between infrastructure and application concerns
    5. Startup-time dependency validation prevents runtime configuration errors

    Architectural Decision: Custom Container vs Pure FastAPI Depends()
    ================================================================
    While FastAPI's Depends() is more idiomatic, this container approach is chosen for:

    - **Protocol Enforcement**: Forces infrastructure to register Protocol implementations,
      maintaining clean hexagonal architecture boundaries
    - **Fail-Fast Behavior**: Missing dependencies are caught at startup, not at runtime
    - **Test Simplicity**: Easy dependency substitution without FastAPI override machinery
    - **Explicit Wiring**: Clear visibility of all application dependencies in one place

    The container works WITH FastAPI Depends(), not instead of it:
    - Container manages Protocol registration and lifecycle
    - FastAPI Depends() handles actual injection in route handlers
    - Best of both worlds: architectural control + framework integration

    For simpler applications, pure FastAPI Depends() would suffice.
    For modular systems with Protocol-based architecture, this approach provides better
    separation of concerns and maintainability.
    """

    def __init__(self):
        self._user_repository = None
        self._product_repository = None
        self._ai_content_service = None
        self._mercadolibre_service = None
        self._email_service = None

    # Repository registrations
    def register_user_repository(self, repository):
        """Register user repository implementation."""
        self._user_repository = repository

    def register_product_repository(self, repository):
        """Register product repository implementation."""
        self._product_repository = repository

    def register_ai_content_service(self, service):
        """Register AI content service implementation."""
        self._ai_content_service = service

    def register_mercadolibre_service(self, service):
        """Register MercadoLibre service implementation."""
        self._mercadolibre_service = service

    def register_email_service(self, service):
        """Register email service implementation."""
        self._email_service = service

    # Dependency providers
    def get_user_repository(self):
        """Get user repository dependency."""
        if self._user_repository is None:
            raise RuntimeError("User repository not registered")
        return self._user_repository

    def get_product_repository(self):
        """Get product repository dependency."""
        if self._product_repository is None:
            raise RuntimeError("Product repository not registered")
        return self._product_repository

    def get_ai_content_service(self):
        """Get AI content service dependency."""
        if self._ai_content_service is None:
            raise RuntimeError("AI content service not registered")
        return self._ai_content_service

    def get_mercadolibre_service(self):
        """Get MercadoLibre service dependency."""
        if self._mercadolibre_service is None:
            raise RuntimeError("MercadoLibre service not registered")
        return self._mercadolibre_service

    def get_email_service(self):
        """Get email service dependency."""
        if self._email_service is None:
            raise RuntimeError("Email service not registered")
        return self._email_service


# Global dependency container instance
container = DependencyContainer()


# FastAPI dependency functions
def get_user_repository():
    """FastAPI dependency for user repository."""
    return container.get_user_repository()


def get_product_repository():
    """FastAPI dependency for product repository."""
    return container.get_product_repository()


def get_ai_content_service():
    """FastAPI dependency for AI content service."""
    return container.get_ai_content_service()


def get_mercadolibre_service():
    """FastAPI dependency for MercadoLibre service."""
    return container.get_mercadolibre_service()


def get_email_service():
    """FastAPI dependency for email service."""
    return container.get_email_service()


# Dependency type annotations for FastAPI
# Note: These use Any temporarily - will be replaced with proper Protocol types
# when concrete implementations are created
UserRepositoryDep = Annotated[Any, Depends(get_user_repository)]
ProductRepositoryDep = Annotated[Any, Depends(get_product_repository)]
AIContentServiceDep = Annotated[Any, Depends(get_ai_content_service)]
MercadoLibreServiceDep = Annotated[Any, Depends(get_mercadolibre_service)]
EmailServiceDep = Annotated[Any, Depends(get_email_service)]
