"""Dependency injection configuration for FastAPI."""

from typing import Annotated, Any

from fastapi import Depends, FastAPI

from api.app_factory import create_fastapi_app
from infrastructure.config.logging import get_logger, setup_logging
from infrastructure.config.settings import Settings
from modules.content_generation.domain.ports.ai_service_protocols import (
    AIContentServiceProtocol,
)
from modules.marketplace_integration.domain.ports.mercadolibre_service_protocol import (
    MercadoLibreServiceProtocol,
)
from modules.notifications.domain.ports.email_service_protocol import (
    EmailServiceProtocol,
)
from modules.product_management.domain.ports.product_repository_protocol import (
    ProductRepositoryProtocol,
)
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)


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


class DependencyContainer:
    """Container for managing service dependencies with fail-fast validation."""

    def __init__(self) -> None:
        self._user_repository: UserRepositoryProtocol | None = None
        self._product_repository: ProductRepositoryProtocol | None = None
        self._ai_content_service: AIContentServiceProtocol | None = None
        self._mercadolibre_service: MercadoLibreServiceProtocol | None = None
        self._email_service: EmailServiceProtocol | None = None

    # Repository registrations
    def register_user_repository(self, repository: UserRepositoryProtocol) -> None:
        """Register user repository implementation."""
        self._user_repository = repository

    def register_product_repository(
        self, repository: ProductRepositoryProtocol
    ) -> None:
        """Register product repository implementation."""
        self._product_repository = repository

    def register_ai_content_service(self, service: AIContentServiceProtocol) -> None:
        """Register AI content service implementation."""
        self._ai_content_service = service

    def register_mercadolibre_service(
        self, service: MercadoLibreServiceProtocol
    ) -> None:
        """Register MercadoLibre service implementation."""
        self._mercadolibre_service = service

    def register_email_service(self, service: EmailServiceProtocol) -> None:
        """Register email service implementation."""
        self._email_service = service

    # Dependency providers
    def get_user_repository(self) -> UserRepositoryProtocol:
        """Get user repository dependency."""
        if self._user_repository is None:
            raise RuntimeError("User repository not registered")
        return self._user_repository

    def get_product_repository(self) -> ProductRepositoryProtocol:
        """Get product repository dependency."""
        if self._product_repository is None:
            raise RuntimeError("Product repository not registered")
        return self._product_repository

    def get_ai_content_service(self) -> AIContentServiceProtocol:
        """Get AI content service dependency."""
        if self._ai_content_service is None:
            raise RuntimeError("AI content service not registered")
        return self._ai_content_service

    def get_mercadolibre_service(self) -> MercadoLibreServiceProtocol:
        """Get MercadoLibre service dependency."""
        if self._mercadolibre_service is None:
            raise RuntimeError("MercadoLibre service not registered")
        return self._mercadolibre_service

    def get_email_service(self) -> EmailServiceProtocol:
        """Get email service dependency."""
        if self._email_service is None:
            raise RuntimeError("Email service not registered")
        return self._email_service


# Global dependency container instance
container = DependencyContainer()


# FastAPI dependency functions
def get_user_repository() -> UserRepositoryProtocol:
    """FastAPI dependency for user repository."""
    return container.get_user_repository()


def get_product_repository() -> ProductRepositoryProtocol:
    """FastAPI dependency for product repository."""
    return container.get_product_repository()


def get_ai_content_service() -> AIContentServiceProtocol:
    """FastAPI dependency for AI content service."""
    return container.get_ai_content_service()


def get_mercadolibre_service() -> MercadoLibreServiceProtocol:
    """FastAPI dependency for MercadoLibre service."""
    return container.get_mercadolibre_service()


def get_email_service() -> EmailServiceProtocol:
    """FastAPI dependency for email service."""
    return container.get_email_service()


# Dependency type annotations for FastAPI routes
UserRepositoryDep = Annotated[UserRepositoryProtocol, Depends(get_user_repository)]
ProductRepositoryDep = Annotated[
    ProductRepositoryProtocol, Depends(get_product_repository)
]
AIContentServiceDep = Annotated[
    AIContentServiceProtocol, Depends(get_ai_content_service)
]
MercadoLibreServiceDep = Annotated[
    MercadoLibreServiceProtocol, Depends(get_mercadolibre_service)
]
EmailServiceDep = Annotated[EmailServiceProtocol, Depends(get_email_service)]


def create_application() -> FastAPI:
    """
    Create and configure the complete FastAPI application with all dependencies.

    This function serves as the main application factory that:
    1. Initializes settings
    2. Sets up logging
    3. Configures the DI container (when implementations are available)
    4. Creates the FastAPI app with all dependencies wired

    Returns:
        Fully configured FastAPI application ready to run
    """
    # Initialize settings
    settings = Settings()

    # Setup logging
    setup_logging(settings)

    # Note: In a real application, you would register actual implementations here
    # For now, the container is available for when implementations are added
    # Example:
    # container.register_user_repository(SQLUserRepository(db))
    # container.register_ai_content_service(OpenAIContentService(settings))

    # Create and return the FastAPI app
    return create_fastapi_app(settings)
