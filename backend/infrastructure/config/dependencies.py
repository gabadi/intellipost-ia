"""
Dependency injection configuration for FastAPI.

This module provides dependency injection setup for the hexagonal architecture,
ensuring loose coupling between layers through Protocol-based interfaces.
"""

from typing import Annotated

from fastapi import Depends

from infrastructure.config.logging import get_logger
from infrastructure.config.settings import Settings


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
LoggerDep = Annotated[any, Depends(get_app_logger)]


# Repository protocol dependencies (to be implemented by infrastructure layer)
class DependencyContainer:
    """
    Container for managing service dependencies.

    This class acts as a registry for Protocol implementations,
    allowing the infrastructure layer to register concrete implementations
    that the application layer can use through dependency injection.
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
UserRepositoryDep = Annotated[
    any, Depends(get_user_repository)
]  # Will be typed when implemented
ProductRepositoryDep = Annotated[any, Depends(get_product_repository)]
AIContentServiceDep = Annotated[any, Depends(get_ai_content_service)]
MercadoLibreServiceDep = Annotated[any, Depends(get_mercadolibre_service)]
EmailServiceDep = Annotated[any, Depends(get_email_service)]
