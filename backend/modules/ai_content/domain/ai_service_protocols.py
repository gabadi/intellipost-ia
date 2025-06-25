"""
AI service protocols for hexagonal architecture.

This module defines Protocol interfaces for AI-related services,
ensuring loose coupling between domain logic and AI service implementations.
"""

from typing import Protocol

from modules.product.domain.confidence_score import ConfidenceScore


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
