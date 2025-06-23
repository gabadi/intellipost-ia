"""
Domain service protocols for hexagonal architecture.

This module defines abstract base classes for domain services that contain
business logic and orchestrate interactions between entities and external services.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.product import Product
from domain.entities.user import User


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
