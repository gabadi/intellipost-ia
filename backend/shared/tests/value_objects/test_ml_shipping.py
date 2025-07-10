"""
Tests for MercadoLibre shipping value object.
"""

from decimal import Decimal

import pytest

from shared.value_objects.exceptions import (
    InvalidFieldRangeError,
    InvalidFieldTypeError,
    InvalidFieldValueError,
    RequiredFieldError,
)
from shared.value_objects.mercadolibre.shipping import MLShipping, MLShippingMethod

pytestmark = pytest.mark.unit


class TestMLShippingMethod:
    """Test cases for MLShippingMethod."""

    def test_valid_shipping_method_creation(self):
        """Test creating a valid ML shipping method."""
        method = MLShippingMethod(
            id=123, name="Standard", cost=Decimal("100.00"), currency_id="ARS"
        )

        assert method.id == 123
        assert method.name == "Standard"
        assert method.cost == Decimal("100.00")
        assert method.currency_id == "ARS"

    def test_shipping_method_with_optional_costs(self):
        """Test shipping method with optional cost fields."""
        method = MLShippingMethod(
            id=123,
            name="Express",
            cost=Decimal("200.00"),
            currency_id="ARS",
            list_cost=Decimal("250.00"),
            option_cost=Decimal("50.00"),
        )

        assert method.list_cost == Decimal("250.00")
        assert method.option_cost == Decimal("50.00")

    def test_shipping_method_missing_name(self):
        """Test shipping method creation with missing name."""
        with pytest.raises(RequiredFieldError):
            MLShippingMethod(id=123, name="", cost=Decimal("100.00"))

    def test_shipping_method_negative_cost(self):
        """Test shipping method creation with negative cost."""
        with pytest.raises(InvalidFieldRangeError):
            MLShippingMethod(id=123, name="Standard", cost=Decimal("-10.00"))

    def test_shipping_method_negative_list_cost(self):
        """Test shipping method creation with negative list cost."""
        with pytest.raises(InvalidFieldRangeError):
            MLShippingMethod(
                id=123,
                name="Standard",
                cost=Decimal("100.00"),
                list_cost=Decimal("-10.00"),
            )


class TestMLShipping:
    """Test cases for MLShipping."""

    def test_valid_shipping_creation(self):
        """Test creating valid ML shipping."""
        method = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))

        shipping = MLShipping(
            mode="me2", free_shipping=False, methods=[method], local_pick_up=True
        )

        assert shipping.mode == "me2"
        assert not shipping.free_shipping
        assert len(shipping.methods) == 1
        assert shipping.local_pick_up
        assert shipping.has_methods()
        assert shipping.get_method_count() == 1

    def test_free_shipping_creation(self):
        """Test creating free shipping."""
        shipping = MLShipping.create_free_shipping()

        assert shipping.mode == "me1"
        assert shipping.free_shipping
        assert shipping.is_free_shipping()
        assert shipping.get_shipping_cost() == Decimal("0")

    def test_not_specified_shipping(self):
        """Test creating not specified shipping."""
        shipping = MLShipping.not_specified()

        assert shipping.mode == "not_specified"
        assert not shipping.free_shipping
        assert not shipping.has_methods()

    def test_custom_shipping_creation(self):
        """Test creating custom shipping."""
        shipping = MLShipping.custom_shipping(Decimal("150.00"), "USD")

        assert shipping.mode == "custom"
        assert shipping.cost == Decimal("150.00")
        assert shipping.currency_id == "USD"
        assert shipping.get_shipping_cost() == Decimal("150.00")

    def test_invalid_shipping_mode(self):
        """Test shipping creation with invalid mode."""
        with pytest.raises(InvalidFieldValueError):
            MLShipping(mode="invalid_mode")

    def test_validation_invalid_methods_type(self):
        """Test validation with invalid methods type."""
        with pytest.raises(InvalidFieldTypeError):
            MLShipping(mode="me2", methods="not a list")

    def test_validation_invalid_method_in_list(self):
        """Test validation with invalid method in list."""
        with pytest.raises(InvalidFieldTypeError):
            MLShipping(mode="me2", methods=["not a shipping method"])

    def test_validation_invalid_tags_type(self):
        """Test validation with invalid tags type."""
        with pytest.raises(InvalidFieldTypeError):
            MLShipping(mode="me1", tags="not a list")

    def test_validation_invalid_tag_in_list(self):
        """Test validation with invalid tag in list."""
        with pytest.raises(InvalidFieldTypeError):
            MLShipping(mode="me1", tags=[123])  # Should be strings

    def test_validation_invalid_dimensions_type(self):
        """Test validation with invalid dimensions type."""
        with pytest.raises(InvalidFieldTypeError):
            MLShipping(mode="me1", dimensions="not a dict")

    def test_validation_negative_cost(self):
        """Test validation with negative cost."""
        with pytest.raises(InvalidFieldRangeError):
            MLShipping(mode="custom", cost=Decimal("-10.00"))

    def test_validate_field(self):
        """Test field validation."""
        shipping = MLShipping(mode="me1")

        # Valid mode
        shipping.validate_field("mode", "me2")

        # Invalid mode
        with pytest.raises(InvalidFieldValueError):
            shipping.validate_field("mode", "invalid")

        # Valid free_shipping
        shipping.validate_field("free_shipping", True)

        # Invalid free_shipping type
        with pytest.raises(InvalidFieldTypeError):
            shipping.validate_field("free_shipping", "yes")

        # Valid methods
        method = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))
        shipping.validate_field("methods", [method])

        # Invalid methods type
        with pytest.raises(InvalidFieldTypeError):
            shipping.validate_field("methods", "not a list")

    def test_get_method_by_id(self):
        """Test getting method by ID."""
        method1 = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))
        method2 = MLShippingMethod(id=456, name="Express", cost=Decimal("200.00"))

        shipping = MLShipping(mode="me2", methods=[method1, method2])

        found_method = shipping.get_method_by_id(123)
        assert found_method == method1

        not_found = shipping.get_method_by_id(999)
        assert not_found is None

    def test_add_method(self):
        """Test adding a shipping method."""
        method1 = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))
        shipping = MLShipping(mode="me2", methods=[method1])

        method2 = MLShippingMethod(id=456, name="Express", cost=Decimal("200.00"))
        updated_shipping = shipping.add_method(method2)

        # Original should be unchanged
        assert len(shipping.methods) == 1

        # New instance should have both
        assert len(updated_shipping.methods) == 2
        assert updated_shipping.get_method_by_id(123) is not None
        assert updated_shipping.get_method_by_id(456) is not None

    def test_add_method_to_empty_methods(self):
        """Test adding method when methods is None."""
        shipping = MLShipping(mode="me1")
        method = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))

        updated_shipping = shipping.add_method(method)

        assert shipping.methods is None
        assert len(updated_shipping.methods) == 1

    def test_remove_method(self):
        """Test removing a shipping method."""
        method1 = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))
        method2 = MLShippingMethod(id=456, name="Express", cost=Decimal("200.00"))
        shipping = MLShipping(mode="me2", methods=[method1, method2])

        updated_shipping = shipping.remove_method(123)

        # Original should be unchanged
        assert len(shipping.methods) == 2

        # New instance should have one less
        assert len(updated_shipping.methods) == 1
        assert updated_shipping.get_method_by_id(123) is None
        assert updated_shipping.get_method_by_id(456) is not None

    def test_remove_nonexistent_method(self):
        """Test removing a non-existent method."""
        method = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))
        shipping = MLShipping(mode="me2", methods=[method])

        updated_shipping = shipping.remove_method(999)

        # Should return the same instance
        assert updated_shipping == shipping

    def test_remove_method_from_empty_methods(self):
        """Test removing method when methods is None."""
        shipping = MLShipping(mode="me1")

        updated_shipping = shipping.remove_method(123)

        # Should return the same instance
        assert updated_shipping == shipping

    def test_to_ml_api_format(self):
        """Test converting to MercadoLibre API format."""
        method = MLShippingMethod(
            id=123,
            name="Standard",
            cost=Decimal("100.00"),
            currency_id="ARS",
            list_cost=Decimal("120.00"),
        )

        shipping = MLShipping(
            mode="me2",
            free_shipping=False,
            methods=[method],
            tags=["fulfillment"],
            dimensions={"weight": "1.5", "width": "10", "height": "5", "length": "15"},
            local_pick_up=True,
            cost=Decimal("100.00"),
            currency_id="ARS",
        )

        result = shipping.to_ml_api_format()

        assert result["mode"] == "me2"
        assert result["free_shipping"] is False
        assert result["local_pick_up"] is True
        assert result["cost"] == 100.0
        assert result["currency_id"] == "ARS"
        assert result["tags"] == ["fulfillment"]
        assert result["dimensions"] == {
            "weight": "1.5",
            "width": "10",
            "height": "5",
            "length": "15",
        }

        assert len(result["methods"]) == 1
        method_data = result["methods"][0]
        assert method_data["id"] == 123
        assert method_data["name"] == "Standard"
        assert method_data["cost"] == 100.0
        assert method_data["list_cost"] == 120.0

    def test_from_ml_api_format(self):
        """Test creating from MercadoLibre API format."""
        api_data = {
            "mode": "me2",
            "free_shipping": False,
            "methods": [
                {
                    "id": 123,
                    "name": "Standard",
                    "cost": 100.0,
                    "currency_id": "ARS",
                    "list_cost": 120.0,
                }
            ],
            "tags": ["fulfillment"],
            "dimensions": {"weight": "1.5"},
            "local_pick_up": True,
            "cost": 100.0,
            "currency_id": "ARS",
        }

        shipping = MLShipping.from_ml_api_format(api_data)

        assert shipping.mode == "me2"
        assert not shipping.free_shipping
        assert shipping.local_pick_up
        assert shipping.cost == Decimal("100.0")
        assert shipping.currency_id == "ARS"
        assert shipping.tags == ["fulfillment"]
        assert shipping.dimensions == {"weight": "1.5"}

        assert len(shipping.methods) == 1
        method = shipping.methods[0]
        assert method.id == 123
        assert method.name == "Standard"
        assert method.cost == Decimal("100.0")
        assert method.list_cost == Decimal("120.0")

    def test_from_ml_api_format_missing_mode(self):
        """Test creating from API format with missing mode."""
        with pytest.raises(RequiredFieldError):
            MLShipping.from_ml_api_format({})

    def test_validate_ml_constraints(self):
        """Test MercadoLibre-specific constraints validation."""
        # Valid shipping
        shipping = MLShipping(mode="me1", free_shipping=True)
        shipping.validate_ml_constraints()

        # Valid me2 with methods
        method = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))
        shipping_me2 = MLShipping(mode="me2", methods=[method])
        shipping_me2.validate_ml_constraints()

    def test_validate_ml_constraints_me1_with_cost(self):
        """Test ML constraints for me1 mode with cost."""
        # Invalid: free shipping with cost > 0
        with pytest.raises(InvalidFieldValueError):
            shipping = MLShipping(
                mode="me1", free_shipping=True, cost=Decimal("100.00")
            )
            shipping.validate_ml_constraints()

    def test_validate_ml_constraints_me2_without_methods(self):
        """Test ML constraints for me2 mode without methods."""
        with pytest.raises(InvalidFieldValueError):
            shipping = MLShipping(mode="me2")
            shipping.validate_ml_constraints()

    def test_validate_ml_constraints_custom_without_cost(self):
        """Test ML constraints for custom mode without cost."""
        with pytest.raises(InvalidFieldValueError):
            shipping = MLShipping(mode="custom")
            shipping.validate_ml_constraints()

    def test_validate_ml_constraints_invalid_currency(self):
        """Test ML constraints with invalid currency."""
        with pytest.raises(InvalidFieldValueError):
            shipping = MLShipping(
                mode="custom", cost=Decimal("100.00"), currency_id="INVALID"
            )
            shipping.validate_ml_constraints()

    def test_validate_ml_constraints_invalid_dimensions(self):
        """Test ML constraints with invalid dimensions."""
        with pytest.raises(InvalidFieldRangeError):
            shipping = MLShipping(
                mode="me1",
                dimensions={"weight": "-1.0"},  # Negative weight
            )
            shipping.validate_ml_constraints()

    def test_validate_ml_constraints_invalid_tags(self):
        """Test ML constraints with invalid tags."""
        with pytest.raises(InvalidFieldValueError):
            shipping = MLShipping(mode="me1", tags=["invalid_tag"])
            shipping.validate_ml_constraints()

    def test_has_local_pickup(self):
        """Test checking if local pickup is available."""
        shipping_with_pickup = MLShipping(mode="me1", local_pick_up=True)
        assert shipping_with_pickup.has_local_pickup()

        shipping_without_pickup = MLShipping(mode="me1", local_pick_up=False)
        assert not shipping_without_pickup.has_local_pickup()

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        method = MLShippingMethod(id=123, name="Standard", cost=Decimal("100.00"))

        original = MLShipping(
            mode="me2",
            free_shipping=False,
            methods=[method],
            tags=["fulfillment"],
            local_pick_up=True,
            cost=Decimal("100.00"),
        )

        # Convert to dict
        data = original.to_dict()

        # Convert back
        restored = MLShipping.from_dict(data)

        assert original == restored
        assert restored.mode == "me2"
        assert len(restored.methods) == 1
        assert restored.tags == ["fulfillment"]

    def test_json_serialization(self):
        """Test JSON serialization."""
        shipping = MLShipping(mode="me1", free_shipping=True)

        # To JSON
        json_str = shipping.to_json()

        # From JSON
        restored = MLShipping.from_json(json_str)

        assert shipping == restored
        assert restored.mode == "me1"
        assert restored.free_shipping
