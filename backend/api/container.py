"""
API-owned dependency injection container.

This container manages API-owned protocols and their implementations.
It does NOT import protocols from modules, only from the API layer.
"""

from typing import Annotated

from fastapi import Depends

from api.protocols.authentication_provider import AuthenticationProviderProtocol
from api.protocols.content_provider import ContentProviderProtocol
from api.protocols.product_provider import ProductProviderProtocol
from infrastructure.config.settings import Settings


class APIContainer:
    """
    API-owned dependency injection container.

    This container only knows about API-owned protocols and their implementations.
    It does NOT import or know about module-internal protocols.
    """

    def __init__(self) -> None:
        self._authentication_provider: AuthenticationProviderProtocol | None = None
        self._product_provider: ProductProviderProtocol | None = None
        self._content_provider: ContentProviderProtocol | None = None

    def register_authentication_provider(
        self, provider: AuthenticationProviderProtocol
    ) -> None:
        """Register authentication provider implementation."""
        self._authentication_provider = provider

    def register_product_provider(self, provider: ProductProviderProtocol) -> None:
        """Register product provider implementation."""
        self._product_provider = provider

    def register_content_provider(self, provider: ContentProviderProtocol) -> None:
        """Register content provider implementation."""
        self._content_provider = provider

    def get_authentication_provider(self) -> AuthenticationProviderProtocol:
        """Get authentication provider dependency."""
        if self._authentication_provider is None:
            raise RuntimeError("Authentication provider not registered")
        return self._authentication_provider

    def get_product_provider(self) -> ProductProviderProtocol:
        """Get product provider dependency."""
        if self._product_provider is None:
            raise RuntimeError("Product provider not registered")
        return self._product_provider

    def get_content_provider(self) -> ContentProviderProtocol:
        """Get content provider dependency."""
        if self._content_provider is None:
            raise RuntimeError("Content provider not registered")
        return self._content_provider


# Global API container instance
api_container = APIContainer()


# Settings dependency
def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# FastAPI dependency functions
def get_authentication_provider() -> AuthenticationProviderProtocol:
    """FastAPI dependency for authentication provider."""
    return api_container.get_authentication_provider()


def get_product_provider() -> ProductProviderProtocol:
    """FastAPI dependency for product provider."""
    return api_container.get_product_provider()


def get_content_provider() -> ContentProviderProtocol:
    """FastAPI dependency for content provider."""
    return api_container.get_content_provider()


# Dependency type annotations for FastAPI routes
SettingsDep = Annotated[Settings, Depends(get_settings)]
AuthenticationProviderDep = Annotated[
    AuthenticationProviderProtocol, Depends(get_authentication_provider)
]
ProductProviderDep = Annotated[ProductProviderProtocol, Depends(get_product_provider)]
ContentProviderDep = Annotated[ContentProviderProtocol, Depends(get_content_provider)]
