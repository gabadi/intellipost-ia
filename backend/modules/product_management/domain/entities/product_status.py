"""
Product status definitions.

This module contains the product status enumeration and related logic.
"""

from enum import Enum


class ProductStatus(Enum):
    """Product processing status enumeration."""

    UPLOADING = "uploading"  # Images being uploaded
    PROCESSING = "processing"  # AI content generation in progress
    READY = "ready"  # Generated content ready for review
    PUBLISHING = "publishing"  # Being published to MercadoLibre
    PUBLISHED = "published"  # Successfully published
    FAILED = "failed"  # Processing or publishing failed
