"""Protocols for cross-module communication and coordination."""

from typing import Any, Protocol
from uuid import UUID


class UserProviderProtocol(Protocol):
    """Protocol for user management operations across modules."""

    async def get_user_by_id(self, user_id: UUID) -> Any:
        """Get user by ID."""
        ...

    async def authenticate_user(self, email: str, password: str) -> Any:
        """Authenticate user credentials."""
        ...


class ProductProviderProtocol(Protocol):
    """Protocol for product management operations across modules."""

    async def get_product_by_id(self, product_id: UUID) -> Any:
        """Get product by ID."""
        ...

    async def create_product(self, user_id: UUID, product_data: Any) -> Any:
        """Create new product."""
        ...


class ContentGenerationProtocol(Protocol):
    """Protocol for AI content generation across modules."""

    async def generate_content(self, product_data: Any) -> Any:
        """Generate AI content for product."""
        ...

    async def assess_content_quality(self, content: Any) -> float:
        """Assess generated content quality score."""
        ...


class MarketplaceIntegrationProtocol(Protocol):
    """Protocol for marketplace publishing across modules."""

    async def publish_to_marketplace(self, product_id: UUID, content: Any) -> Any:
        """Publish product to external marketplace."""
        ...

    async def sync_marketplace_status(self, product_id: UUID) -> Any:
        """Sync product status from marketplace."""
        ...
