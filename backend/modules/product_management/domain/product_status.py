"""
Product status definitions.

This module contains the product status enumeration and related logic.
"""

from enum import Enum


class ProductStatus(Enum):
    """Product processing status enumeration."""

    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    PUBLISHED = "published"
    FAILED = "failed"
    DRAFT = "draft"
