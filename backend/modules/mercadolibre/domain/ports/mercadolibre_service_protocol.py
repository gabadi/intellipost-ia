"""MercadoLibre service port (protocol) for hexagonal architecture.

Defines the contract for MercadoLibre marketplace integration capabilities
required by the domain. Infrastructure layer provides concrete implementations (adapters).
"""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from modules.product.domain.product import Product


class MercadoLibreServiceProtocol(Protocol):
    """Port for MercadoLibre marketplace integration.

    Defines the contract that infrastructure adapters must implement
    to provide MercadoLibre API capabilities to the domain.
    """

    async def authenticate_user(self, auth_code: str) -> dict[str, str]:
        """Authenticate user with MercadoLibre OAuth.

        Args:
            auth_code: OAuth authorization code from MercadoLibre

        Returns:
            Dictionary containing access_token, refresh_token, user_id
        """
        ...

    async def refresh_token(self, refresh_token: str) -> dict[str, str]:
        """Refresh MercadoLibre access token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dictionary containing new access_token and refresh_token
        """
        ...

    async def get_user_info(self, access_token: str) -> dict[str, str]:
        """Get user information from MercadoLibre.

        Args:
            access_token: Valid access token

        Returns:
            Dictionary containing user_id, nickname, email
        """
        ...

    async def get_categories(self, site_id: str) -> list[dict[str, str]]:
        """Get product categories for a site.

        Args:
            site_id: MercadoLibre site identifier (e.g., 'MLA', 'MLB')

        Returns:
            List of category dictionaries with id and name
        """
        ...

    async def create_listing(
        self, product: "Product", access_token: str, category_id: str
    ) -> str:
        """Create a new product listing.

        Args:
            product: Product domain entity to list
            access_token: Valid access token
            category_id: MercadoLibre category identifier

        Returns:
            MercadoLibre listing ID
        """
        ...

    async def update_listing(
        self, listing_id: str, product: "Product", access_token: str
    ) -> bool:
        """Update an existing product listing.

        Args:
            listing_id: MercadoLibre listing identifier
            product: Updated product domain entity
            access_token: Valid access token

        Returns:
            True if listing was updated successfully
        """
        ...
