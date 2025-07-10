"""
Tests for migration DTOs.

This module tests the migration DTOs that provide type-safe migration
operations while maintaining backward compatibility.
"""

from decimal import Decimal

import pytest

from shared.migration.dtos import (
    GeneratedContentMigrationData,
    MLAttributesMigrationData,
    MLSaleTermsMigrationData,
    MLShippingMigrationData,
    ValidationMigrationData,
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestMLAttributesMigrationData:
    """Test ML attributes migration DTO."""

    def test_from_dict_empty(self):
        """Test creating DTO from empty dict."""
        migration_data = MLAttributesMigrationData.from_dict({})

        assert migration_data.is_empty()
        assert not migration_data.has_new_format()
        assert not migration_data.has_legacy_format()
        assert migration_data.validate() == []

    def test_from_dict_new_format(self):
        """Test creating DTO from new format dict."""
        data = {
            "attributes": {
                "BRAND": {"id": "BRAND", "name": "Brand", "value_name": "Nike"}
            }
        }
        migration_data = MLAttributesMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert migration_data.has_new_format()
        assert not migration_data.has_legacy_format()
        assert migration_data.validate() == []

    def test_from_dict_legacy_format(self):
        """Test creating DTO from legacy format dict."""
        data = {"brand": "Nike", "color": "Red"}
        migration_data = MLAttributesMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert not migration_data.has_new_format()
        assert migration_data.has_legacy_format()
        assert migration_data.validate() == []

    def test_validation_errors(self):
        """Test validation with invalid data."""
        migration_data = MLAttributesMigrationData(
            raw_data="invalid",  # Should be dict
            attributes=None,
        )

        errors = migration_data.validate()
        assert len(errors) == 1
        assert "raw_data must be a dictionary" in errors[0]


class TestMLSaleTermsMigrationData:
    """Test ML sale terms migration DTO."""

    def test_from_dict_empty(self):
        """Test creating DTO from empty dict."""
        migration_data = MLSaleTermsMigrationData.from_dict({})

        assert migration_data.is_empty()
        assert not migration_data.has_new_format()
        assert not migration_data.has_legacy_format()
        assert migration_data.validate() == []

    def test_from_dict_new_format(self):
        """Test creating DTO from new format dict."""
        data = {
            "sale_terms": {
                "WARRANTY_TYPE": {
                    "id": "WARRANTY_TYPE",
                    "name": "Warranty Type",
                    "value_name": "Manufacturer warranty",
                }
            }
        }
        migration_data = MLSaleTermsMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert migration_data.has_new_format()
        assert not migration_data.has_legacy_format()
        assert migration_data.validate() == []

    def test_from_dict_legacy_format(self):
        """Test creating DTO from legacy format dict."""
        data = {"warranty": "1 year", "return_policy": "30 days"}
        migration_data = MLSaleTermsMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert not migration_data.has_new_format()
        assert migration_data.has_legacy_format()
        assert migration_data.validate() == []


class TestMLShippingMigrationData:
    """Test ML shipping migration DTO."""

    def test_from_dict_empty(self):
        """Test creating DTO from empty dict."""
        migration_data = MLShippingMigrationData.from_dict({})

        assert migration_data.is_empty()
        assert migration_data.validate() == []

    def test_from_dict_with_cost(self):
        """Test creating DTO with cost data."""
        data = {
            "mode": "me1",
            "cost": "100.50",
            "currency_id": "ARS",
            "free_shipping": True,
        }
        migration_data = MLShippingMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert migration_data.mode == "me1"
        assert migration_data.cost == Decimal("100.50")
        assert migration_data.currency_id == "ARS"
        assert migration_data.free_shipping is True
        assert migration_data.validate() == []

    def test_from_dict_with_invalid_cost(self):
        """Test creating DTO with invalid cost."""
        data = {
            "mode": "me1",
            "cost": "invalid",  # Should be numeric
            "currency_id": "ARS",
        }
        migration_data = MLShippingMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert migration_data.cost is None  # Should be None due to conversion error
        assert migration_data.validate() == []

    def test_from_dict_with_methods(self):
        """Test creating DTO with methods."""
        data = {
            "mode": "me2",
            "methods": [{"id": 1, "name": "Standard", "cost": "50.00"}],
        }
        migration_data = MLShippingMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert migration_data.methods is not None
        assert len(migration_data.methods) == 1
        assert migration_data.validate() == []

    def test_validation_errors(self):
        """Test validation with invalid data."""
        migration_data = MLShippingMigrationData(
            raw_data="invalid",  # Should be dict
            methods="invalid",  # Should be list
        )

        errors = migration_data.validate()
        assert len(errors) >= 1
        assert "raw_data must be a dictionary" in errors[0]


class TestGeneratedContentMigrationData:
    """Test generated content migration DTO."""

    def test_from_dict_empty(self):
        """Test creating DTO from empty dict."""
        migration_data = GeneratedContentMigrationData.from_dict({})

        assert migration_data.is_empty()
        assert not migration_data.has_ml_attributes()
        assert not migration_data.has_ml_sale_terms()
        assert not migration_data.has_ml_shipping()
        assert migration_data.validate() == []

    def test_from_dict_complete(self):
        """Test creating DTO from complete dict."""
        data = {
            "id": "123",
            "title": "Test Product",
            "ml_price": "100.50",
            "ml_attributes": {"brand": "Nike"},
            "ml_sale_terms": {"warranty": "1 year"},
            "ml_shipping": {"mode": "me1"},
        }
        migration_data = GeneratedContentMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert migration_data.id == "123"
        assert migration_data.title == "Test Product"
        assert migration_data.ml_price == Decimal("100.50")
        assert migration_data.has_ml_attributes()
        assert migration_data.has_ml_sale_terms()
        assert migration_data.has_ml_shipping()
        assert migration_data.validate() == []

    def test_from_dict_invalid_price(self):
        """Test creating DTO with invalid price."""
        data = {
            "id": "123",
            "ml_price": "invalid",  # Should be numeric
        }
        migration_data = GeneratedContentMigrationData.from_dict(data)

        assert not migration_data.is_empty()
        assert migration_data.ml_price is None  # Should be None due to conversion error
        assert migration_data.validate() == []

    def test_validation_errors(self):
        """Test validation with invalid data."""
        migration_data = GeneratedContentMigrationData(
            raw_data="invalid",  # Should be dict
            ml_attributes="invalid",  # Should be dict if not None
        )

        errors = migration_data.validate()
        assert len(errors) >= 1
        assert "raw_data must be a dictionary" in errors[0]


class TestValidationMigrationData:
    """Test validation migration DTO."""

    def test_create_with_defaults(self):
        """Test creating validation data with defaults."""
        original_data = {"id": "123", "title": "Test"}
        migrated_data = {
            "id": "123",
            "title": "Test",
            "ml_attributes": {},
            "ml_sale_terms": {},
            "ml_shipping": {},
        }

        validation_data = ValidationMigrationData.create(original_data, migrated_data)

        assert validation_data.is_valid()
        assert validation_data.validate() == []

    def test_create_with_custom_fields(self):
        """Test creating validation data with custom fields."""
        original_data = {"custom_field": "value"}
        migrated_data = {"custom_field": "value"}

        validation_data = ValidationMigrationData.create(
            original_data,
            migrated_data,
            essential_fields=["custom_field"],
            value_object_fields=[],  # No value object fields required
        )

        assert validation_data.is_valid()
        assert validation_data.validate() == []

    def test_validation_missing_essential_field(self):
        """Test validation with missing essential field."""
        original_data = {"id": "123"}
        migrated_data = {}  # Missing id

        validation_data = ValidationMigrationData.create(original_data, migrated_data)

        assert not validation_data.is_valid()
        errors = validation_data.validate()
        assert len(errors) >= 1
        assert any("Migration lost essential field: id" in error for error in errors)

    def test_validation_changed_essential_field(self):
        """Test validation with changed essential field."""
        original_data = {"id": "123"}
        migrated_data = {"id": "456"}  # Changed id

        validation_data = ValidationMigrationData.create(original_data, migrated_data)

        assert not validation_data.is_valid()
        errors = validation_data.validate()
        assert len(errors) >= 1
        assert any("Migration changed essential field: id" in error for error in errors)

    def test_validation_missing_value_object_field(self):
        """Test validation with missing value object field."""
        original_data = {"id": "123"}
        migrated_data = {"id": "123"}  # Missing value object fields

        validation_data = ValidationMigrationData.create(original_data, migrated_data)

        assert not validation_data.is_valid()
        errors = validation_data.validate()
        assert len(errors) == 3  # Missing all 3 value object fields
        assert "Migration missing value object field: ml_attributes" in errors[0]
        assert "Migration missing value object field: ml_sale_terms" in errors[1]
        assert "Migration missing value object field: ml_shipping" in errors[2]

    def test_validation_invalid_data_types(self):
        """Test validation with invalid data types."""
        validation_data = ValidationMigrationData(
            original_data="invalid",  # Should be dict
            migrated_data=123,  # Should be dict
        )

        assert not validation_data.is_valid()
        errors = validation_data.validate()
        assert len(errors) >= 1
        assert "original_data must be a dictionary" in errors[0]
        if len(errors) > 1:
            assert "migrated_data must be a dictionary" in errors[1]
