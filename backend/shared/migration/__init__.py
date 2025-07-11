"""
Migration utilities for backward compatibility.

This module provides utilities to migrate from legacy dict-based
data structures to type-safe value objects using typed DTOs.
"""

from .dtos import (
    GeneratedContentMigrationData,
    MLAttributesMigrationData,
    MLSaleTermsMigrationData,
    MLShippingMigrationData,
    ValidationMigrationData,
)
from .value_object_migration import (
    migrate_generated_content_from_dict,
    migrate_ml_attributes_from_dict,
    migrate_ml_sale_terms_from_dict,
    migrate_ml_shipping_from_dict,
)

__all__ = [
    # Migration functions
    "migrate_ml_attributes_from_dict",
    "migrate_ml_sale_terms_from_dict",
    "migrate_ml_shipping_from_dict",
    "migrate_generated_content_from_dict",
    # Migration DTOs
    "MLAttributesMigrationData",
    "MLSaleTermsMigrationData",
    "MLShippingMigrationData",
    "GeneratedContentMigrationData",
    "ValidationMigrationData",
]
