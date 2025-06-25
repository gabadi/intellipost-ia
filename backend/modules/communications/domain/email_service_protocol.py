"""
Email service protocol for hexagonal architecture.

This module defines Protocol interface for email notification services,
ensuring loose coupling between domain logic and external services.
"""

from typing import Any, Protocol


class EmailServiceProtocol(Protocol):
    """Protocol for email notification services."""

    async def send_verification_email(self, user: Any, verification_link: str) -> bool:
        """Send email verification message."""
        ...

    async def send_notification(self, user: Any, subject: str, content: str) -> bool:
        """Send general notification email."""
        ...

    async def send_product_published_notification(
        self, user: Any, product: Any
    ) -> bool:
        """Send notification when product is published."""
        ...
