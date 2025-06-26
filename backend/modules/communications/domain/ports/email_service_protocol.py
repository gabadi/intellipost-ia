"""Email service port (protocol) for hexagonal architecture.

Defines the contract for email notification capabilities required by the domain.
Infrastructure layer provides concrete implementations (adapters).
"""

from typing import Protocol


class EmailServiceProtocol(Protocol):
    """Port for email notification services.

    Defines the contract that infrastructure adapters must implement
    to provide email capabilities to the domain.
    """

    async def send_verification_email(
        self, to_email: str, verification_link: str, user_name: str | None = None
    ) -> bool:
        """Send email verification message.

        Args:
            to_email: Recipient email address
            verification_link: URL for email verification
            user_name: Optional user name for personalization

        Returns:
            True if email was sent successfully
        """
        ...

    async def send_notification(
        self, to_email: str, subject: str, content: str, content_type: str = "text/html"
    ) -> bool:
        """Send general notification email.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            content: Email body content
            content_type: MIME type (text/html or text/plain)

        Returns:
            True if email was sent successfully
        """
        ...

    async def send_product_published_notification(
        self, to_email: str, product_title: str, product_url: str | None = None
    ) -> bool:
        """Send notification when product is published.

        Args:
            to_email: Recipient email address
            product_title: Name of the published product
            product_url: Optional URL to view the product

        Returns:
            True if email was sent successfully
        """
        ...
