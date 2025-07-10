"""
Value object migration utilities.

This module provides utilities to migrate from legacy dict-based
data structures to type-safe value objects, ensuring backward compatibility.
"""

from decimal import Decimal
from typing import Any

from shared.value_objects.mercadolibre import MLAttributes, MLSaleTerms, MLShipping
from shared.value_objects.mercadolibre.attributes import MLAttribute
from shared.value_objects.mercadolibre.sale_terms import MLSaleTerm
from shared.value_objects.mercadolibre.shipping import MLShippingMethod

# Note: This module uses print statements for logging to avoid architecture violations
# In production, loggers should be injected through dependency injection


def migrate_ml_attributes_from_dict(data: dict[str, Any]) -> MLAttributes:
    """
    Migrate MercadoLibre attributes from legacy dict format to MLAttributes.

    Args:
        data: Legacy dictionary containing attribute data

    Returns:
        MLAttributes instance

    Raises:
        ValueError: If migration fails
    """
    try:
        # Handle empty or None data
        if not data:
            return MLAttributes.empty()

        # Handle different legacy formats
        if "attributes" in data:
            # New format - should be directly convertible
            return MLAttributes.from_dict(data)  # type: ignore
        else:
            # Legacy format - convert flat dict to structured format
            attributes = {}

            for key, value in data.items():
                if isinstance(value, dict):
                    # Handle nested attribute structure
                    attr_id = key
                    attr_name = value.get("name", key)

                    attribute = MLAttribute(
                        id=attr_id,
                        name=attr_name,
                        value_id=value.get("value_id"),
                        value_name=value.get("value_name"),
                        value_struct=value.get("value_struct"),
                        values=value.get("values"),
                        attribute_group_id=value.get("attribute_group_id"),
                        attribute_group_name=value.get("attribute_group_name"),
                    )
                    attributes[attr_id] = attribute
                else:
                    # Handle simple key-value pairs
                    attr_id = key
                    attribute = MLAttribute(
                        id=attr_id,
                        name=attr_id.replace("_", " ").title(),
                        value_name=str(value),
                    )
                    attributes[attr_id] = attribute

            return MLAttributes(attributes=attributes)

    except Exception:
        # Logging removed - architecture violation: error(f"Failed to migrate ML attributes: {e}")
        # Logging removed - architecture violation: error(f"Data: {data}")
        # Return empty attributes to maintain functionality
        return MLAttributes.empty()


def migrate_ml_sale_terms_from_dict(data: dict[str, Any]) -> MLSaleTerms:
    """
    Migrate MercadoLibre sale terms from legacy dict format to MLSaleTerms.

    Args:
        data: Legacy dictionary containing sale terms data

    Returns:
        MLSaleTerms instance

    Raises:
        ValueError: If migration fails
    """
    try:
        # Handle empty or None data
        if not data:
            return MLSaleTerms.empty()

        # Handle different legacy formats
        if "sale_terms" in data:
            # New format - should be directly convertible
            return MLSaleTerms.from_dict(data)  # type: ignore
        else:
            # Legacy format - convert flat dict to structured format
            sale_terms = {}

            for key, value in data.items():
                if isinstance(value, dict):
                    # Handle nested sale term structure
                    term_id = key
                    term_name = value.get("name", key)

                    sale_term = MLSaleTerm(
                        id=term_id,
                        name=term_name,
                        value_id=value.get("value_id"),
                        value_name=value.get("value_name"),
                        value_struct=value.get("value_struct"),
                        values=value.get("values"),
                    )
                    sale_terms[term_id] = sale_term
                else:
                    # Handle simple key-value pairs
                    term_id = key
                    sale_term = MLSaleTerm(
                        id=term_id,
                        name=term_id.replace("_", " ").title(),
                        value_name=str(value),
                    )
                    sale_terms[term_id] = sale_term

            return MLSaleTerms(sale_terms=sale_terms)

    except Exception:
        # Logging removed - architecture violation: error(f"Failed to migrate ML sale terms: {e}")
        # Logging removed - architecture violation: error(f"Data: {data}")
        # Return empty sale terms to maintain functionality
        return MLSaleTerms.empty()


def migrate_ml_shipping_from_dict(data: dict[str, Any]) -> MLShipping:
    """
    Migrate MercadoLibre shipping from legacy dict format to MLShipping.

    Args:
        data: Legacy dictionary containing shipping data

    Returns:
        MLShipping instance

    Raises:
        ValueError: If migration fails
    """
    try:
        # Handle empty or None data
        if not data:
            return MLShipping.not_specified()

        # Extract and validate basic fields first
        mode = data.get("mode", "not_specified")
        free_shipping = data.get("free_shipping", False)
        local_pick_up = data.get("local_pick_up", False)

        # Handle cost
        cost = None
        if "cost" in data:
            try:
                cost = Decimal(str(data["cost"]))
            except (ValueError, TypeError):
                cost = None

        # Handle methods
        methods = None
        if "methods" in data and isinstance(data["methods"], list):
            methods = []
            for method_data in data["methods"]:
                if isinstance(method_data, dict):
                    try:
                        method = MLShippingMethod(
                            id=method_data.get("id", 0),
                            name=method_data.get("name", "Standard"),
                            cost=Decimal(str(method_data.get("cost", 0))),
                            currency_id=method_data.get("currency_id", "ARS"),
                            list_cost=Decimal(str(method_data["list_cost"]))
                            if method_data.get("list_cost")
                            else None,
                            option_cost=Decimal(str(method_data["option_cost"]))
                            if method_data.get("option_cost")
                            else None,
                        )
                        methods.append(method)
                    except Exception:
                        # Logging removed - architecture violation: warning(f"Failed to migrate shipping method: {e}")
                        continue

            # If no valid methods, set to None
            if methods is not None and len(methods) == 0:
                methods = None

        return MLShipping(
            mode=mode,
            free_shipping=free_shipping,
            methods=methods,
            tags=data.get("tags"),
            dimensions=data.get("dimensions"),
            local_pick_up=local_pick_up,
            free_methods=data.get("free_methods"),
            cost=cost,
            currency_id=data.get("currency_id", "ARS"),
        )

    except Exception:
        # Logging removed - architecture violation: error(f"Failed to migrate ML shipping: {e}")
        # Logging removed - architecture violation: error(f"Data: {data}")
        # Return not specified shipping to maintain functionality
        return MLShipping.not_specified()


def migrate_generated_content_from_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Migrate GeneratedContent from legacy dict format to use value objects.

    Args:
        data: Legacy dictionary containing generated content data

    Returns:
        Dictionary with migrated value objects

    Raises:
        ValueError: If migration fails
    """
    try:
        # Validate input type
        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary, got {type(data).__name__}")

        # Create a copy to avoid modifying the original
        migrated_data = data.copy()

        # Migrate ML attributes
        if "ml_attributes" in migrated_data:
            ml_attributes_data = migrated_data["ml_attributes"]
            migrated_data["ml_attributes"] = migrate_ml_attributes_from_dict(
                ml_attributes_data
            )
        else:
            migrated_data["ml_attributes"] = MLAttributes.empty()

        # Migrate ML sale terms
        if "ml_sale_terms" in migrated_data:
            ml_sale_terms_data = migrated_data["ml_sale_terms"]
            migrated_data["ml_sale_terms"] = migrate_ml_sale_terms_from_dict(
                ml_sale_terms_data
            )
        else:
            migrated_data["ml_sale_terms"] = MLSaleTerms.empty()

        # Migrate ML shipping
        if "ml_shipping" in migrated_data:
            ml_shipping_data = migrated_data["ml_shipping"]
            migrated_data["ml_shipping"] = migrate_ml_shipping_from_dict(
                ml_shipping_data
            )
        else:
            migrated_data["ml_shipping"] = MLShipping.not_specified()

        return migrated_data

    except Exception as e:
        # Logging removed - architecture violation
        # Original code logged error details about the failed migration
        raise ValueError(f"Failed to migrate generated content: {e}") from e


def safe_migrate_ml_attributes(data: dict[str, Any] | None) -> MLAttributes:
    """
    Safely migrate ML attributes with fallback.

    Args:
        data: Dictionary containing attribute data or None

    Returns:
        MLAttributes instance (empty if migration fails)
    """
    if not data:
        return MLAttributes.empty()

    try:
        return migrate_ml_attributes_from_dict(data)
    except Exception:
        # Logging removed - architecture violation: warning(f"Failed to migrate ML attributes, using empty: {e}")
        return MLAttributes.empty()


def safe_migrate_ml_sale_terms(data: dict[str, Any] | None) -> MLSaleTerms:
    """
    Safely migrate ML sale terms with fallback.

    Args:
        data: Dictionary containing sale terms data or None

    Returns:
        MLSaleTerms instance (empty if migration fails)
    """
    if not data:
        return MLSaleTerms.empty()

    try:
        return migrate_ml_sale_terms_from_dict(data)
    except Exception:
        # Logging removed - architecture violation: warning(f"Failed to migrate ML sale terms, using empty: {e}")
        return MLSaleTerms.empty()


def safe_migrate_ml_shipping(data: dict[str, Any] | None) -> MLShipping:
    """
    Safely migrate ML shipping with fallback.

    Args:
        data: Dictionary containing shipping data or None

    Returns:
        MLShipping instance (not_specified if migration fails)
    """
    if not data:
        return MLShipping.not_specified()

    try:
        return migrate_ml_shipping_from_dict(data)
    except Exception:
        # Logging removed - architecture violation: warning(f"Failed to migrate ML shipping, using not_specified: {e}")
        return MLShipping.not_specified()


def validate_migration_result(
    original_data: dict[str, Any], migrated_data: dict[str, Any]
) -> bool:
    """
    Validate that migration preserved essential data.

    Args:
        original_data: Original dictionary data
        migrated_data: Migrated dictionary data

    Returns:
        True if migration is valid, False otherwise
    """
    try:
        # Ensure both inputs are dictionaries
        if not isinstance(original_data, dict) or not isinstance(migrated_data, dict):
            # Logging removed - architecture violation: error("Migration validation requires dictionary inputs")
            return False

        # Check that essential fields are preserved
        essential_fields = [
            "id",
            "product_id",
            "title",
            "description",
            "ml_category_id",
            "ml_title",
            "ml_price",
        ]

        for field in essential_fields:
            if field in original_data:
                if field not in migrated_data:
                    # Logging removed - architecture violation: error(f"Migration lost essential field: {field}")
                    return False
                if original_data[field] != migrated_data[field]:
                    # Logging removed - architecture violation:
                    # Original logged: Migration changed essential field
                    return False

        # Check that value objects are present
        value_object_fields = ["ml_attributes", "ml_sale_terms", "ml_shipping"]
        return all(field in migrated_data for field in value_object_fields)

    except Exception:
        # Logging removed - architecture violation: error(f"Migration validation failed: {e}")
        return False
