"""
Value object migration service for content generation domain.

This service handles the migration from legacy dict-based data structures
to typed value objects while respecting architectural boundaries.
"""

from typing import Any

from shared.migration.value_object_migration import (
    safe_migrate_ml_attributes,
    safe_migrate_ml_sale_terms,
    safe_migrate_ml_shipping,
)
from shared.value_objects.mercadolibre import MLAttributes, MLSaleTerms, MLShipping


class ValueObjectMigrationService:
    """Service for migrating legacy data to value objects."""

    def migrate_ml_attributes(self, data: dict[str, Any] | None) -> MLAttributes:
        """
        Migrate ML attributes from legacy format.

        Args:
            data: Legacy attribute data

        Returns:
            MLAttributes value object
        """
        return safe_migrate_ml_attributes(data)

    def migrate_ml_sale_terms(self, data: dict[str, Any] | None) -> MLSaleTerms:
        """
        Migrate ML sale terms from legacy format.

        Args:
            data: Legacy sale terms data

        Returns:
            MLSaleTerms value object
        """
        return safe_migrate_ml_sale_terms(data)

    def migrate_ml_shipping(self, data: dict[str, Any] | None) -> MLShipping:
        """
        Migrate ML shipping from legacy format.

        Args:
            data: Legacy shipping data

        Returns:
            MLShipping value object
        """
        return safe_migrate_ml_shipping(data)
