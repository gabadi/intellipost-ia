"""
MercadoLibre service protocol for hexagonal architecture.

This module defines Protocol interface for MercadoLibre API integration,
ensuring loose coupling between domain logic and external services.

Architectural Decision: Protocol in Domain Layer
==============================================

**PR Review Question**: "this is not a protocol? why in domain?"

**Answer**: This IS a Python Protocol (typing.Protocol) and belongs in the domain for:

1. **Hexagonal Architecture**: Domain defines interfaces (ports) that infrastructure implements
2. **Dependency Inversion**: Domain doesn't depend on infrastructure, infrastructure depends on domain
3. **Business Contract**: Protocol represents what the domain needs, not how it's implemented
4. **Testing**: Domain can be tested without external dependencies
5. **Flexibility**: Multiple implementations can satisfy the same domain contract

Protocol Placement in Hexagonal Architecture:
- Domain Layer: Defines WHAT is needed (Protocol/Port)
- Infrastructure Layer: Defines HOW it's implemented (Adapter)
- Application Layer: Uses the protocol without knowing the implementation

This follows the "Ports and Adapters" pattern where ports (protocols) are defined
by the domain and adapters (implementations) are provided by infrastructure.
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
