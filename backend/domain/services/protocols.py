"""
Domain service protocols for hexagonal architecture.

This module defines Protocol interfaces that external services must implement,
ensuring loose coupling between domain logic and infrastructure concerns.
"""

from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from domain.entities.product import ConfidenceScore, Product
from domain.entities.user import User


class UserRepositoryProtocol(Protocol):
    """Protocol for user data persistence operations."""

    async def create(self, user: User) -> User:
        """Create a new user."""
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        ...

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        ...

    async def update(self, user: User) -> User:
        """Update an existing user."""
        ...

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        ...


class ProductRepositoryProtocol(Protocol):
    """Protocol for product data persistence operations."""

    async def create(self, product: Product) -> Product:
        """Create a new product."""
        ...

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        ...

    async def get_by_user_id(self, user_id: UUID) -> list[Product]:
        """Get all products for a user."""
        ...

    async def update(self, product: Product) -> Product:
        """Update an existing product."""
        ...

    async def delete(self, product_id: UUID) -> bool:
        """Delete a product by ID."""
        ...


class AIContentServiceProtocol(Protocol):
    """Protocol for AI content generation services."""

    async def generate_title(self, product_info: str) -> str:
        """Generate an optimized title for a product."""
        ...

    async def generate_description(self, product_info: str) -> str:
        """Generate a detailed description for a product."""
        ...

    async def generate_tags(self, product_info: str) -> list[str]:
        """Generate relevant tags for a product."""
        ...

    async def calculate_confidence(self, generated_content: dict) -> ConfidenceScore:
        """Calculate confidence score for generated content."""
        ...


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


# Domain service interfaces (business logic)
class UserDomainService(ABC):
    """Abstract base class for user domain services."""

    @abstractmethod
    async def register_user(self, email: str, password: str) -> User:
        """Register a new user."""
        ...

    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user credentials."""
        ...

    @abstractmethod
    async def verify_email(self, user_id: UUID, verification_token: str) -> bool:
        """Verify user's email address."""
        ...


class ProductDomainService(ABC):
    """Abstract base class for product domain services."""

    @abstractmethod
    async def create_product(self, user_id: UUID, product_data: dict) -> Product:
        """Create a new product."""
        ...

    @abstractmethod
    async def process_product_content(self, product_id: UUID) -> Product:
        """Process product with AI content generation."""
        ...

    @abstractmethod
    async def publish_to_mercadolibre(self, product_id: UUID) -> Product:
        """Publish product to MercadoLibre."""
        ...


class NotificationDomainService(ABC):
    """Abstract base class for notification domain services."""

    @abstractmethod
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user."""
        ...

    @abstractmethod
    async def notify_product_status_change(self, user: User, product: Product) -> bool:
        """Notify user of product status changes."""
        ...
