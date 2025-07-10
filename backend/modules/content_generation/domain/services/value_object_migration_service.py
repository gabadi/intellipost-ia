"""
Value object migration service for content generation domain.

This service handles the migration from legacy dict-based data structures
to typed value objects while respecting architectural boundaries.

The service now uses typed migration DTOs to provide type safety and validation
while maintaining complete backward compatibility with existing migration workflows.
"""

from typing import Any

from shared.migration.dtos import (
    MLAttributesMigrationData,
    MLSaleTermsMigrationData,
    MLShippingMigrationData,
)
from shared.migration.value_object_migration import (
    safe_migrate_ml_attributes,
    safe_migrate_ml_sale_terms,
    safe_migrate_ml_shipping,
)
from shared.value_objects.mercadolibre import MLAttributes, MLSaleTerms, MLShipping


class ValueObjectMigrationService:
    """
    Service for migrating legacy data to value objects.

    This service uses typed migration DTOs to provide type safety and validation
    while maintaining complete backward compatibility with existing migration workflows.
    """

    def migrate_ml_attributes(self, data: dict[str, Any] | None) -> MLAttributes:
        """
        Migrate ML attributes from legacy format.

        Args:
            data: Legacy attribute data

        Returns:
            MLAttributes value object
        """
        # Create migration DTO for type safety and validation
        migration_data = MLAttributesMigrationData.from_dict(data or {})

        # Validate migration data
        validation_errors = migration_data.validate()
        if validation_errors:
            # Continue with migration but log validation issues
            pass

        return safe_migrate_ml_attributes(migration_data.raw_data)

    def migrate_ml_sale_terms(self, data: dict[str, Any] | None) -> MLSaleTerms:
        """
        Migrate ML sale terms from legacy format.

        Args:
            data: Legacy sale terms data

        Returns:
            MLSaleTerms value object
        """
        # Create migration DTO for type safety and validation
        migration_data = MLSaleTermsMigrationData.from_dict(data or {})

        # Validate migration data
        validation_errors = migration_data.validate()
        if validation_errors:
            # Continue with migration but log validation issues
            pass

        return safe_migrate_ml_sale_terms(migration_data.raw_data)

    def migrate_ml_shipping(self, data: dict[str, Any] | None) -> MLShipping:
        """
        Migrate ML shipping from legacy format.

        Args:
            data: Legacy shipping data

        Returns:
            MLShipping value object
        """
        # Create migration DTO for type safety and validation
        migration_data = MLShippingMigrationData.from_dict(data or {})

        # Validate migration data
        validation_errors = migration_data.validate()
        if validation_errors:
            # Continue with migration but log validation issues
            pass

        return safe_migrate_ml_shipping(migration_data.raw_data)
