"""
MercadoLibre service protocol for hexagonal architecture.

This module defines Protocol interface for MercadoLibre API integration,
ensuring loose coupling between domain logic and external services.
"""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from modules.product.domain.product import Product


class MercadoLibreServiceProtocol(Protocol):
    """Protocol for MercadoLibre API integration."""

    async def authenticate_user(self, auth_code: str) -> dict:
        """Authenticate user with MercadoLibre OAuth."""
        ...

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh MercadoLibre access token."""
        ...

    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from MercadoLibre."""
        ...

    async def get_categories(self, site_id: str) -> list[dict]:
        """Get product categories for a site."""
        ...

    async def create_listing(self, product: "Product", access_token: str) -> str:
        """Create a new product listing."""
        ...

    async def update_listing(
        self, listing_id: str, product: "Product", access_token: str
    ) -> bool:
        """Update an existing product listing."""
        ...
