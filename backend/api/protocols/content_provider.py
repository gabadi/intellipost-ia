"""
Content provider protocol for API layer.

This protocol defines what the API needs for content generation functionality.
"""

from typing import Protocol
from uuid import UUID

from pydantic import BaseModel


class ContentGenerationRequest(BaseModel):
    """Request for content generation."""

    product_id: UUID
    content_type: str  # "title", "description", "tags", etc.
    parameters: dict[str, str] | None = None


class GeneratedContent(BaseModel):
    """Generated content result."""

    content_id: UUID
    product_id: UUID
    content_type: str
    content: str
    confidence_score: float
    created_at: str  # ISO format


class ContentProviderProtocol(Protocol):
    """
    Protocol defining content generation capabilities that the API requires.

    This protocol is owned by the API layer and defines what content generation
    functionality the API needs from modules.
    """

    async def generate_content(
        self, request: ContentGenerationRequest
    ) -> GeneratedContent:
        """
        Generate content for a product.

        Args:
            request: Content generation request

        Returns:
            Generated content result

        Raises:
            ContentGenerationError: If generation fails
        """
        ...

    async def get_content(self, content_id: UUID) -> GeneratedContent | None:
        """
        Retrieve generated content by ID.

        Args:
            content_id: Content identifier

        Returns:
            Generated content if found, None otherwise
        """
        ...
