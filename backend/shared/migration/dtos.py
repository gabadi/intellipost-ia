"""
Migration DTOs for type-safe migration operations.

This module provides typed DTOs for migration scenarios, replacing
dict[str, Any] parameters with specific migration DTOs while maintaining
complete backward compatibility for migration utilities.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class MLAttributesMigrationData:
    """
    DTO for ML attributes migration data.

    Provides typed access to ML attributes migration data while maintaining
    backward compatibility with legacy dict-based formats.
    """

    raw_data: dict[str, Any]  # Keep original for safety and compatibility
    id: str | None = None
    name: str | None = None
    value_id: str | None = None
    value_name: str | None = None
    value_struct: dict[str, Any] | None = None
    values: list[dict[str, Any]] | None = None
    attribute_group_id: str | None = None
    attribute_group_name: str | None = None
    attributes: dict[str, Any] | None = None  # For new format with nested attributes

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MLAttributesMigrationData":
        """
        Create migration data from dictionary with safe field extraction.

        Args:
            data: Dictionary containing migration data

        Returns:
            MLAttributesMigrationData instance
        """
        if not data:
            return cls(raw_data={})

        return cls(
            raw_data=data.copy(),
            id=data.get("id"),
            name=data.get("name"),
            value_id=data.get("value_id"),
            value_name=data.get("value_name"),
            value_struct=data.get("value_struct"),
            values=data.get("values"),
            attribute_group_id=data.get("attribute_group_id"),
            attribute_group_name=data.get("attribute_group_name"),
            attributes=data.get("attributes"),
        )

    def is_empty(self) -> bool:
        """Check if migration data is empty."""
        return not self.raw_data

    def has_new_format(self) -> bool:
        """Check if data uses new format with nested attributes."""
        return "attributes" in self.raw_data

    def has_legacy_format(self) -> bool:
        """Check if data uses legacy flat format."""
        return not self.has_new_format() and bool(self.raw_data)

    def validate(self) -> list[str]:
        """
        Validate migration data and return list of validation errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not isinstance(self.raw_data, dict):
            errors.append("raw_data must be a dictionary")
            return errors

        if self.has_new_format():
            if not isinstance(self.attributes, dict):
                errors.append("attributes field must be a dictionary in new format")

        return errors


@dataclass(frozen=True)
class MLSaleTermsMigrationData:
    """
    DTO for ML sale terms migration data.

    Provides typed access to ML sale terms migration data while maintaining
    backward compatibility with legacy dict-based formats.
    """

    raw_data: dict[str, Any]  # Keep original for safety and compatibility
    id: str | None = None
    name: str | None = None
    value_id: str | None = None
    value_name: str | None = None
    value_struct: dict[str, Any] | None = None
    values: list[dict[str, Any]] | None = None
    sale_terms: dict[str, Any] | None = None  # For new format with nested sale terms

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MLSaleTermsMigrationData":
        """
        Create migration data from dictionary with safe field extraction.

        Args:
            data: Dictionary containing migration data

        Returns:
            MLSaleTermsMigrationData instance
        """
        if not data:
            return cls(raw_data={})

        return cls(
            raw_data=data.copy(),
            id=data.get("id"),
            name=data.get("name"),
            value_id=data.get("value_id"),
            value_name=data.get("value_name"),
            value_struct=data.get("value_struct"),
            values=data.get("values"),
            sale_terms=data.get("sale_terms"),
        )

    def is_empty(self) -> bool:
        """Check if migration data is empty."""
        return not self.raw_data

    def has_new_format(self) -> bool:
        """Check if data uses new format with nested sale terms."""
        return "sale_terms" in self.raw_data

    def has_legacy_format(self) -> bool:
        """Check if data uses legacy flat format."""
        return not self.has_new_format() and bool(self.raw_data)

    def validate(self) -> list[str]:
        """
        Validate migration data and return list of validation errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not isinstance(self.raw_data, dict):
            errors.append("raw_data must be a dictionary")
            return errors

        if self.has_new_format():
            if not isinstance(self.sale_terms, dict):
                errors.append("sale_terms field must be a dictionary in new format")

        return errors


@dataclass(frozen=True)
class MLShippingMigrationData:
    """
    DTO for ML shipping migration data.

    Provides typed access to ML shipping migration data while maintaining
    backward compatibility with legacy dict-based formats.
    """

    raw_data: dict[str, Any]  # Keep original for safety and compatibility
    mode: str | None = None
    free_shipping: bool | None = None
    local_pick_up: bool | None = None
    cost: Decimal | None = None
    currency_id: str | None = None
    methods: list[dict[str, Any]] | None = None
    tags: list[str] | None = None
    dimensions: dict[str, Any] | None = None
    free_methods: list[dict[str, Any]] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MLShippingMigrationData":
        """
        Create migration data from dictionary with safe field extraction.

        Args:
            data: Dictionary containing migration data

        Returns:
            MLShippingMigrationData instance
        """
        if not data:
            return cls(raw_data={})

        # Safe cost conversion
        cost = None
        if "cost" in data:
            try:
                cost = Decimal(str(data["cost"])) if data["cost"] is not None else None
            except (ValueError, TypeError, Exception):
                cost = None

        return cls(
            raw_data=data.copy(),
            mode=data.get("mode"),
            free_shipping=data.get("free_shipping"),
            local_pick_up=data.get("local_pick_up"),
            cost=cost,
            currency_id=data.get("currency_id"),
            methods=data.get("methods"),
            tags=data.get("tags"),
            dimensions=data.get("dimensions"),
            free_methods=data.get("free_methods"),
        )

    def is_empty(self) -> bool:
        """Check if migration data is empty."""
        return not self.raw_data

    def validate(self) -> list[str]:
        """
        Validate migration data and return list of validation errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not isinstance(self.raw_data, dict):
            errors.append("raw_data must be a dictionary")
            return errors

        # Validate methods if present
        if self.methods is not None:
            if not isinstance(self.methods, list):
                errors.append("methods must be a list")
            else:
                for i, method in enumerate(self.methods):
                    if not isinstance(method, dict):
                        errors.append(f"methods[{i}] must be a dictionary")

        # Validate cost (skip if it's already a Decimal - from_dict handles conversion)
        if self.cost is not None and not isinstance(self.cost, Decimal):
            errors.append("cost must be a Decimal or convertible to Decimal")

        return errors


@dataclass(frozen=True)
class GeneratedContentMigrationData:
    """
    DTO for generated content migration data.

    Provides typed access to generated content migration data, handling
    migration of complex content structures with nested value objects.
    """

    raw_data: dict[str, Any]  # Keep original for safety and compatibility
    id: str | None = None
    product_id: str | None = None
    title: str | None = None
    description: str | None = None
    ml_category_id: str | None = None
    ml_title: str | None = None
    ml_price: Decimal | None = None
    ml_attributes: dict[str, Any] | None = None
    ml_sale_terms: dict[str, Any] | None = None
    ml_shipping: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GeneratedContentMigrationData":
        """
        Create migration data from dictionary with safe field extraction.

        Args:
            data: Dictionary containing migration data

        Returns:
            GeneratedContentMigrationData instance
        """
        if not data:
            return cls(raw_data={})

        # Safe price conversion
        ml_price = None
        if "ml_price" in data:
            try:
                ml_price = (
                    Decimal(str(data["ml_price"]))
                    if data["ml_price"] is not None
                    else None
                )
            except (ValueError, TypeError, Exception):
                ml_price = None

        return cls(
            raw_data=data.copy(),
            id=data.get("id"),
            product_id=data.get("product_id"),
            title=data.get("title"),
            description=data.get("description"),
            ml_category_id=data.get("ml_category_id"),
            ml_title=data.get("ml_title"),
            ml_price=ml_price,
            ml_attributes=data.get("ml_attributes"),
            ml_sale_terms=data.get("ml_sale_terms"),
            ml_shipping=data.get("ml_shipping"),
        )

    def is_empty(self) -> bool:
        """Check if migration data is empty."""
        return not self.raw_data

    def has_ml_attributes(self) -> bool:
        """Check if ML attributes data is present."""
        return self.ml_attributes is not None

    def has_ml_sale_terms(self) -> bool:
        """Check if ML sale terms data is present."""
        return self.ml_sale_terms is not None

    def has_ml_shipping(self) -> bool:
        """Check if ML shipping data is present."""
        return self.ml_shipping is not None

    def validate(self) -> list[str]:
        """
        Validate migration data and return list of validation errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not isinstance(self.raw_data, dict):
            errors.append("raw_data must be a dictionary")
            return errors

        # Validate price (skip if it's already a Decimal - from_dict handles conversion)
        if self.ml_price is not None and not isinstance(self.ml_price, Decimal):
            errors.append("ml_price must be a Decimal or convertible to Decimal")

        # Validate nested structures
        for field_name, field_value in [
            ("ml_attributes", self.ml_attributes),
            ("ml_sale_terms", self.ml_sale_terms),
            ("ml_shipping", self.ml_shipping),
        ]:
            if field_value is not None and not isinstance(field_value, dict):
                errors.append(f"{field_name} must be a dictionary")

        return errors


@dataclass(frozen=True)
class ValidationMigrationData:
    """
    DTO for migration validation operations.

    Provides typed access to original and migrated data for validation
    purposes, ensuring migration integrity and data preservation.
    """

    original_data: dict[str, Any]
    migrated_data: dict[str, Any]
    essential_fields: list[str] | None = None
    value_object_fields: list[str] | None = None

    @classmethod
    def create(
        cls,
        original_data: dict[str, Any],
        migrated_data: dict[str, Any],
        essential_fields: list[str] | None = None,
        value_object_fields: list[str] | None = None,
    ) -> "ValidationMigrationData":
        """
        Create validation migration data with defaults.

        Args:
            original_data: Original dictionary data
            migrated_data: Migrated dictionary data
            essential_fields: Fields that must be preserved (uses defaults if None)
            value_object_fields: Value object fields to check (uses defaults if None)

        Returns:
            ValidationMigrationData instance
        """
        default_essential_fields = [
            "id",
            "product_id",
            "title",
            "description",
            "ml_category_id",
            "ml_title",
            "ml_price",
        ]

        default_value_object_fields = [
            "ml_attributes",
            "ml_sale_terms",
            "ml_shipping",
        ]

        return cls(
            original_data=original_data.copy() if original_data else {},
            migrated_data=migrated_data.copy() if migrated_data else {},
            essential_fields=essential_fields
            if essential_fields is not None
            else default_essential_fields,
            value_object_fields=value_object_fields
            if value_object_fields is not None
            else default_value_object_fields,
        )

    def validate(self) -> list[str]:
        """
        Validate migration data preservation and return list of validation errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate input types
        if not isinstance(self.original_data, dict):
            errors.append("original_data must be a dictionary")

        if not isinstance(self.migrated_data, dict):
            errors.append("migrated_data must be a dictionary")

        # If basic validation fails, return early
        if errors:
            return errors

        # Check essential fields preservation
        if self.essential_fields:
            for field in self.essential_fields:
                if field in self.original_data:
                    if field not in self.migrated_data:
                        errors.append(f"Migration lost essential field: {field}")
                    elif self.original_data[field] != self.migrated_data[field]:
                        errors.append(f"Migration changed essential field: {field}")

        # Check value object fields presence
        if self.value_object_fields:
            for field in self.value_object_fields:
                if field not in self.migrated_data:
                    errors.append(f"Migration missing value object field: {field}")

        return errors

    def is_valid(self) -> bool:
        """Check if migration validation passes."""
        return len(self.validate()) == 0
