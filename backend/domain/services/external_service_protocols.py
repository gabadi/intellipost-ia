"""
External service protocols for hexagonal architecture.

This module defines Protocol interfaces for external service integrations,
ensuring loose coupling between domain logic and external services.
"""

from typing import Protocol

from domain.entities.product import Product
from domain.entities.user import User


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

    async def create_listing(self, product: Product, access_token: str) -> str:
        """Create a new product listing."""
        ...

    async def update_listing(
        self, listing_id: str, product: Product, access_token: str
    ) -> bool:
        """Update an existing product listing."""
        ...


class EmailServiceProtocol(Protocol):
    """Protocol for email notification services."""

    async def send_verification_email(self, user: User, verification_link: str) -> bool:
        """Send email verification message."""
        ...

    async def send_notification(self, user: User, subject: str, content: str) -> bool:
        """Send general notification email."""
        ...

    async def send_product_published_notification(
        self, user: User, product: Product
    ) -> bool:
        """Send notification when product is published."""
        ...
