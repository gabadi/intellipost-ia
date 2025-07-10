"""
Tests for migration utilities.
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from shared.migration.value_object_migration import (
    migrate_generated_content_from_dict,
    migrate_ml_attributes_from_dict,
    migrate_ml_sale_terms_from_dict,
    migrate_ml_shipping_from_dict,
    safe_migrate_ml_attributes,
    safe_migrate_ml_sale_terms,
    safe_migrate_ml_shipping,
    validate_migration_result,
)
from shared.value_objects.mercadolibre import MLAttributes, MLSaleTerms, MLShipping

pytestmark = pytest.mark.unit


class TestMLAttributesMigration:
    """Test cases for ML attributes migration."""

    def test_migrate_empty_attributes(self):
        """Test migrating empty attributes."""
        result = migrate_ml_attributes_from_dict({})
        assert result.is_empty()

        result_none = migrate_ml_attributes_from_dict(None)
        assert result_none.is_empty()

    def test_migrate_new_format_attributes(self):
        """Test migrating attributes in new format."""
        data = {
            "attributes": {
                "BRAND": {"id": "BRAND", "name": "Marca", "value_name": "Nike"}
            }
        }

        result = migrate_ml_attributes_from_dict(data)
        assert not result.is_empty()
        assert result.has_attribute("BRAND")
        assert result.get_attribute_value("BRAND") == "Nike"

    def test_migrate_legacy_flat_format(self):
        """Test migrating attributes from legacy flat format."""
        data = {"BRAND": {"name": "Marca", "value_name": "Nike"}, "COLOR": "Rojo"}

        result = migrate_ml_attributes_from_dict(data)
        assert not result.is_empty()
        assert result.has_attribute("BRAND")
        assert result.has_attribute("COLOR")
        assert result.get_attribute_value("BRAND") == "Nike"
        assert result.get_attribute_value("COLOR") == "Rojo"

    def test_migrate_legacy_simple_format(self):
        """Test migrating simple key-value pairs."""
        data = {"brand": "Nike", "color": "Red", "size": "42"}

        result = migrate_ml_attributes_from_dict(data)
        assert not result.is_empty()
        assert result.has_attribute("brand")
        assert result.get_attribute_value("brand") == "Nike"

    def test_safe_migrate_attributes_with_invalid_data(self):
        """Test safe migration with invalid data."""
        # Should not raise exception, return empty instead
        result = safe_migrate_ml_attributes("invalid data")
        assert result.is_empty()


class TestMLSaleTermsMigration:
    """Test cases for ML sale terms migration."""

    def test_migrate_empty_sale_terms(self):
        """Test migrating empty sale terms."""
        result = migrate_ml_sale_terms_from_dict({})
        assert result.is_empty()

        result_none = migrate_ml_sale_terms_from_dict(None)
        assert result_none.is_empty()

    def test_migrate_new_format_sale_terms(self):
        """Test migrating sale terms in new format."""
        data = {
            "sale_terms": {
                "WARRANTY_TYPE": {
                    "id": "WARRANTY_TYPE",
                    "name": "Tipo de garantía",
                    "value_name": "Garantía de fábrica",
                }
            }
        }

        result = migrate_ml_sale_terms_from_dict(data)
        assert not result.is_empty()
        assert result.has_sale_term("WARRANTY_TYPE")
        assert result.get_sale_term_value("WARRANTY_TYPE") == "Garantía de fábrica"

    def test_migrate_legacy_format_sale_terms(self):
        """Test migrating sale terms from legacy format."""
        data = {
            "WARRANTY_TYPE": {
                "name": "Tipo de garantía",
                "value_name": "Garantía de fábrica",
            },
            "WARRANTY_TIME": "12 meses",
        }

        result = migrate_ml_sale_terms_from_dict(data)
        assert not result.is_empty()
        assert result.has_sale_term("WARRANTY_TYPE")
        assert result.has_sale_term("WARRANTY_TIME")

    def test_safe_migrate_sale_terms_with_invalid_data(self):
        """Test safe migration with invalid data."""
        result = safe_migrate_ml_sale_terms("invalid data")
        assert result.is_empty()


class TestMLShippingMigration:
    """Test cases for ML shipping migration."""

    def test_migrate_empty_shipping(self):
        """Test migrating empty shipping."""
        result = migrate_ml_shipping_from_dict({})
        assert result.mode == "not_specified"

        result_none = migrate_ml_shipping_from_dict(None)
        assert result_none.mode == "not_specified"

    def test_migrate_new_format_shipping(self):
        """Test migrating shipping in new format."""
        data = {"mode": "me1", "free_shipping": True, "local_pick_up": False}

        result = migrate_ml_shipping_from_dict(data)
        assert result.mode == "me1"
        assert result.free_shipping
        assert not result.local_pick_up

    def test_migrate_legacy_format_shipping(self):
        """Test migrating shipping from legacy format."""
        data = {
            "free_shipping": True,
            "local_pick_up": True,
            "cost": "150.00",
            "methods": [{"id": 123, "name": "Standard", "cost": 100.0}],
        }

        result = migrate_ml_shipping_from_dict(data)
        assert result.mode == "not_specified"  # Default when not specified
        assert result.free_shipping
        assert result.local_pick_up
        assert result.cost == Decimal("150.00")
        assert len(result.methods) == 1

    def test_migrate_shipping_with_invalid_method(self):
        """Test migrating shipping with invalid method data."""
        data = {
            "mode": "me2",
            "methods": [
                "invalid method data"  # Should be skipped
            ],
        }

        result = migrate_ml_shipping_from_dict(data)
        assert result.mode == "me2"
        assert (
            result.methods is None or len(result.methods) == 0
        )  # Invalid method should be skipped

    def test_safe_migrate_shipping_with_invalid_data(self):
        """Test safe migration with invalid data."""
        result = safe_migrate_ml_shipping("invalid data")
        assert result.mode == "not_specified"


class TestGeneratedContentMigration:
    """Test cases for generated content migration."""

    def test_migrate_generated_content(self):
        """Test migrating complete generated content."""
        product_id = uuid4()
        content_id = uuid4()

        legacy_data = {
            "id": str(content_id),
            "product_id": str(product_id),
            "title": "Test Product",
            "description": "A test product description that is long enough to meet validation requirements.",
            "ml_category_id": "MLA123",
            "ml_category_name": "Electronics",
            "ml_title": "Test Product ML",
            "ml_price": 100.50,
            "ml_currency_id": "ARS",
            "ml_available_quantity": 10,
            "ml_buying_mode": "buy_it_now",
            "ml_condition": "new",
            "ml_listing_type_id": "gold_special",
            "ml_attributes": {"BRAND": {"name": "Marca", "value_name": "Nike"}},
            "ml_sale_terms": {
                "WARRANTY_TYPE": {
                    "name": "Tipo de garantía",
                    "value_name": "Garantía de fábrica",
                }
            },
            "ml_shipping": {"mode": "me1", "free_shipping": True},
            "confidence_overall": 0.85,
            "confidence_breakdown": {"title": 0.9, "description": 0.8},
            "ai_provider": "gemini",
            "ai_model_version": "1.0",
            "generation_time_ms": 1000,
            "version": 1,
            "generated_at": "2024-01-01T00:00:00Z",
        }

        migrated_data = migrate_generated_content_from_dict(legacy_data)

        # Check that value objects were created
        assert isinstance(migrated_data["ml_attributes"], MLAttributes)
        assert isinstance(migrated_data["ml_sale_terms"], MLSaleTerms)
        assert isinstance(migrated_data["ml_shipping"], MLShipping)

        # Check that other fields are preserved
        assert migrated_data["title"] == "Test Product"
        assert migrated_data["ml_price"] == 100.50
        assert migrated_data["confidence_overall"] == 0.85

    def test_migrate_generated_content_with_missing_fields(self):
        """Test migrating content with missing ML fields."""
        content_id = uuid4()
        product_id = uuid4()

        legacy_data = {
            "id": str(content_id),
            "product_id": str(product_id),
            "title": "Test Product",
            "description": "A test product description that is long enough to meet validation requirements.",
            "ml_category_id": "MLA123",
            "ml_category_name": "Electronics",
            "ml_title": "Test Product ML",
            "ml_price": 100.50,
            "ml_currency_id": "ARS",
            "ml_available_quantity": 10,
            "ml_buying_mode": "buy_it_now",
            "ml_condition": "new",
            "ml_listing_type_id": "gold_special",
            "confidence_overall": 0.85,
            "confidence_breakdown": {"title": 0.9, "description": 0.8},
            "ai_provider": "gemini",
            "ai_model_version": "1.0",
            "generation_time_ms": 1000,
            "version": 1,
            "generated_at": "2024-01-01T00:00:00Z",
            # Missing ml_attributes, ml_sale_terms, ml_shipping
        }

        migrated_data = migrate_generated_content_from_dict(legacy_data)

        # Should create empty value objects for missing fields
        assert isinstance(migrated_data["ml_attributes"], MLAttributes)
        assert migrated_data["ml_attributes"].is_empty()

        assert isinstance(migrated_data["ml_sale_terms"], MLSaleTerms)
        assert migrated_data["ml_sale_terms"].is_empty()

        assert isinstance(migrated_data["ml_shipping"], MLShipping)
        assert migrated_data["ml_shipping"].mode == "not_specified"

    def test_migrate_generated_content_with_invalid_data(self):
        """Test migrating content with invalid data."""
        with pytest.raises(ValueError):
            migrate_generated_content_from_dict("invalid data")


class TestMigrationValidation:
    """Test cases for migration validation."""

    def test_validate_migration_result_success(self):
        """Test successful migration validation."""
        original_data = {
            "id": "123",
            "product_id": "456",
            "title": "Test Product",
            "description": "Test description",
            "ml_category_id": "MLA123",
            "ml_title": "Test ML Title",
            "ml_price": 100.50,
            "ml_attributes": {"brand": "Nike"},
            "ml_sale_terms": {"warranty": "1 year"},
            "ml_shipping": {"mode": "me1"},
        }

        migrated_data = original_data.copy()
        migrated_data["ml_attributes"] = MLAttributes.empty()
        migrated_data["ml_sale_terms"] = MLSaleTerms.empty()
        migrated_data["ml_shipping"] = MLShipping.not_specified()

        result = validate_migration_result(original_data, migrated_data)
        assert result is True

    def test_validate_migration_result_missing_field(self):
        """Test migration validation with missing essential field."""
        original_data = {"id": "123", "title": "Test Product"}

        migrated_data = {
            # Missing id field
            "title": "Test Product"
        }

        result = validate_migration_result(original_data, migrated_data)
        assert result is False

    def test_validate_migration_result_changed_field(self):
        """Test migration validation with changed essential field."""
        original_data = {"id": "123", "title": "Test Product"}

        migrated_data = {
            "id": "456",  # Changed value
            "title": "Test Product",
        }

        result = validate_migration_result(original_data, migrated_data)
        assert result is False

    def test_validate_migration_result_missing_value_object(self):
        """Test migration validation with missing value object field."""
        original_data = {"id": "123", "title": "Test Product"}

        migrated_data = {
            "id": "123",
            "title": "Test Product",
            # Missing ml_attributes, ml_sale_terms, ml_shipping
        }

        result = validate_migration_result(original_data, migrated_data)
        assert result is False
