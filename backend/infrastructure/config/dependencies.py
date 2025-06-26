"""Dependency injection configuration for FastAPI."""

from typing import Annotated, Any

from fastapi import Depends

from modules.ai_content.domain.ports.ai_service_protocols import (
    AIContentServiceProtocol,
)
from modules.communications.domain.ports.email_service_protocol import (
    EmailServiceProtocol,
)
from modules.mercadolibre.domain.ports.mercadolibre_service_protocol import (
    MercadoLibreServiceProtocol,
)
from modules.product.domain.ports.product_repository_protocol import (
    ProductRepositoryProtocol,
)
from modules.user.domain.ports.user_repository_protocol import UserRepositoryProtocol

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
