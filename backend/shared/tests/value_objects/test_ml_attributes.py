"""
Tests for MercadoLibre attributes value object.
"""

import pytest

from shared.value_objects.exceptions import (
    InvalidFieldFormatError,
    InvalidFieldTypeError,
    InvalidFieldValueError,
    RequiredFieldError,
)
from shared.value_objects.mercadolibre.attributes import MLAttribute, MLAttributes

pytestmark = pytest.mark.unit


class TestMLAttribute:
    """Test cases for MLAttribute."""

    def test_valid_attribute_creation(self):
        """Test creating a valid ML attribute."""
        attr = MLAttribute(id="BRAND", name="Marca", value_id="123", value_name="Nike")

        assert attr.id == "BRAND"
        assert attr.name == "Marca"
        assert attr.value_id == "123"
        assert attr.value_name == "Nike"

    def test_attribute_with_value_struct(self):
        """Test attribute with value_struct."""
        attr = MLAttribute(
            id="WEIGHT", name="Peso", value_struct={"number": 1.5, "unit": "kg"}
        )

        assert attr.id == "WEIGHT"
        assert attr.name == "Peso"
        assert attr.value_struct == {"number": 1.5, "unit": "kg"}

    def test_attribute_with_values_list(self):
        """Test attribute with values list."""
        attr = MLAttribute(
            id="COLORS",
            name="Colores",
            values=[{"id": "red", "name": "Rojo"}, {"id": "blue", "name": "Azul"}],
        )

        assert attr.id == "COLORS"
        assert attr.name == "Colores"
        assert len(attr.values) == 2

    def test_attribute_missing_id(self):
        """Test attribute creation with missing ID."""
        with pytest.raises(RequiredFieldError):
            MLAttribute(id="", name="Marca", value_name="Nike")

    def test_attribute_missing_name(self):
        """Test attribute creation with missing name."""
        with pytest.raises(RequiredFieldError):
            MLAttribute(id="BRAND", name="", value_name="Nike")

    def test_attribute_missing_value(self):
        """Test attribute creation with no value fields."""
        with pytest.raises(InvalidFieldValueError):
            MLAttribute(id="BRAND", name="Marca")


class TestMLAttributes:
    """Test cases for MLAttributes."""

    def test_valid_attributes_creation(self):
        """Test creating valid ML attributes."""
        attr1 = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attr2 = MLAttribute(id="COLOR", name="Color", value_name="Rojo")

        attributes = MLAttributes(attributes={"BRAND": attr1, "COLOR": attr2})

        assert len(attributes.attributes) == 2
        assert attributes.has_attribute("BRAND")
        assert attributes.has_attribute("COLOR")
        assert not attributes.is_empty()

    def test_empty_attributes(self):
        """Test creating empty ML attributes."""
        attributes = MLAttributes.empty()

        assert len(attributes.attributes) == 0
        assert attributes.is_empty()
        assert attributes.get_attribute_count() == 0

    def test_get_attribute(self):
        """Test getting a specific attribute."""
        attr = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attributes = MLAttributes(attributes={"BRAND": attr})

        retrieved = attributes.get_attribute("BRAND")
        assert retrieved == attr

        not_found = attributes.get_attribute("NONEXISTENT")
        assert not_found is None

    def test_get_attribute_value(self):
        """Test getting attribute value."""
        attr1 = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attr2 = MLAttribute(
            id="WEIGHT", name="Peso", value_struct={"number": 1.5, "unit": "kg"}
        )

        attributes = MLAttributes(attributes={"BRAND": attr1, "WEIGHT": attr2})

        brand_value = attributes.get_attribute_value("BRAND")
        assert brand_value == "Nike"

        weight_value = attributes.get_attribute_value("WEIGHT")
        assert weight_value == {"number": 1.5, "unit": "kg"}

        missing_value = attributes.get_attribute_value("NONEXISTENT")
        assert missing_value is None

    def test_add_attribute(self):
        """Test adding an attribute."""
        attr1 = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attributes = MLAttributes(attributes={"BRAND": attr1})

        attr2 = MLAttribute(id="COLOR", name="Color", value_name="Rojo")
        updated_attributes = attributes.add_attribute(attr2)

        # Original should be unchanged
        assert len(attributes.attributes) == 1

        # New instance should have both
        assert len(updated_attributes.attributes) == 2
        assert updated_attributes.has_attribute("BRAND")
        assert updated_attributes.has_attribute("COLOR")

    def test_remove_attribute(self):
        """Test removing an attribute."""
        attr1 = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attr2 = MLAttribute(id="COLOR", name="Color", value_name="Rojo")
        attributes = MLAttributes(attributes={"BRAND": attr1, "COLOR": attr2})

        updated_attributes = attributes.remove_attribute("BRAND")

        # Original should be unchanged
        assert len(attributes.attributes) == 2

        # New instance should have one less
        assert len(updated_attributes.attributes) == 1
        assert not updated_attributes.has_attribute("BRAND")
        assert updated_attributes.has_attribute("COLOR")

    def test_remove_nonexistent_attribute(self):
        """Test removing a non-existent attribute."""
        attr = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attributes = MLAttributes(attributes={"BRAND": attr})

        updated_attributes = attributes.remove_attribute("NONEXISTENT")

        # Should return the same instance
        assert updated_attributes == attributes

    def test_validation_invalid_attributes_type(self):
        """Test validation with invalid attributes type."""
        with pytest.raises(InvalidFieldTypeError):
            MLAttributes(attributes="not a dict")

    def test_validation_invalid_attribute_in_dict(self):
        """Test validation with invalid attribute in dict."""
        with pytest.raises(InvalidFieldTypeError):
            MLAttributes(attributes={"BRAND": "not an MLAttribute"})

    def test_validation_mismatched_attribute_id(self):
        """Test validation with mismatched attribute ID."""
        attr = MLAttribute(id="BRAND", name="Marca", value_name="Nike")

        with pytest.raises(InvalidFieldValueError):
            MLAttributes(attributes={"COLOR": attr})  # ID mismatch

    def test_validate_field(self):
        """Test field validation."""
        attr = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attributes = MLAttributes(attributes={"BRAND": attr})

        # Valid field
        attributes.validate_field("attributes", {"BRAND": attr})

        # Invalid field type
        with pytest.raises(InvalidFieldTypeError):
            attributes.validate_field("attributes", "not a dict")

        # Invalid attribute in dict
        with pytest.raises(InvalidFieldTypeError):
            attributes.validate_field("attributes", {"BRAND": "not an attribute"})

        # Unknown field
        with pytest.raises(InvalidFieldValueError):
            attributes.validate_field("unknown_field", "value")

    def test_to_ml_api_format(self):
        """Test converting to MercadoLibre API format."""
        attr1 = MLAttribute(id="BRAND", name="Marca", value_id="123", value_name="Nike")
        attr2 = MLAttribute(
            id="WEIGHT", name="Peso", value_struct={"number": 1.5, "unit": "kg"}
        )

        attributes = MLAttributes(attributes={"BRAND": attr1, "WEIGHT": attr2})

        result = attributes.to_ml_api_format()

        assert "attributes" in result
        assert len(result["attributes"]) == 2

        # Check attribute structure
        brand_attr = next(a for a in result["attributes"] if a["id"] == "BRAND")
        assert brand_attr["name"] == "Marca"
        assert brand_attr["value_id"] == "123"
        assert brand_attr["value_name"] == "Nike"

        weight_attr = next(a for a in result["attributes"] if a["id"] == "WEIGHT")
        assert weight_attr["name"] == "Peso"
        assert weight_attr["value_struct"] == {"number": 1.5, "unit": "kg"}

    def test_from_ml_api_format(self):
        """Test creating from MercadoLibre API format."""
        api_data = {
            "attributes": [
                {
                    "id": "BRAND",
                    "name": "Marca",
                    "value_id": "123",
                    "value_name": "Nike",
                },
                {
                    "id": "WEIGHT",
                    "name": "Peso",
                    "value_struct": {"number": 1.5, "unit": "kg"},
                },
            ]
        }

        attributes = MLAttributes.from_ml_api_format(api_data)

        assert len(attributes.attributes) == 2
        assert attributes.has_attribute("BRAND")
        assert attributes.has_attribute("WEIGHT")

        brand_attr = attributes.get_attribute("BRAND")
        assert brand_attr.name == "Marca"
        assert brand_attr.value_name == "Nike"

        weight_attr = attributes.get_attribute("WEIGHT")
        assert weight_attr.name == "Peso"
        assert weight_attr.value_struct == {"number": 1.5, "unit": "kg"}

    def test_from_ml_api_format_missing_attributes(self):
        """Test creating from API format with missing attributes field."""
        with pytest.raises(InvalidFieldValueError):
            MLAttributes.from_ml_api_format({})

    def test_from_ml_api_format_invalid_attribute_data(self):
        """Test creating from API format with invalid attribute data."""
        with pytest.raises(InvalidFieldTypeError):
            MLAttributes.from_ml_api_format({"attributes": ["not a dict"]})

    def test_from_ml_api_format_missing_required_fields(self):
        """Test creating from API format with missing required fields."""
        with pytest.raises(RequiredFieldError):
            MLAttributes.from_ml_api_format(
                {
                    "attributes": [
                        {"name": "Marca"}  # Missing id
                    ]
                }
            )

    def test_validate_ml_constraints(self):
        """Test MercadoLibre-specific constraints validation."""
        # Valid attributes
        attr1 = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attr2 = MLAttribute(id="WEIGHT_KG", name="Peso", value_name="1.5")

        attributes = MLAttributes(attributes={"BRAND": attr1, "WEIGHT_KG": attr2})

        # Should not raise any exception
        attributes.validate_ml_constraints()

    def test_validate_ml_constraints_invalid_id_format(self):
        """Test ML constraints validation with invalid ID format."""
        attr = MLAttribute(id="invalid-id", name="Marca", value_name="Nike")
        attributes = MLAttributes(attributes={"invalid-id": attr})

        with pytest.raises(InvalidFieldFormatError):
            attributes.validate_ml_constraints()

    def test_validate_ml_constraints_long_names(self):
        """Test ML constraints validation with long names."""
        long_name = "a" * 256
        attr = MLAttribute(id="BRAND", name=long_name, value_name="Nike")
        attributes = MLAttributes(attributes={"BRAND": attr})

        with pytest.raises(InvalidFieldValueError):
            attributes.validate_ml_constraints()

    def test_validate_ml_constraints_long_value_name(self):
        """Test ML constraints validation with long value name."""
        long_value_name = "a" * 256
        attr = MLAttribute(id="BRAND", name="Marca", value_name=long_value_name)
        attributes = MLAttributes(attributes={"BRAND": attr})

        with pytest.raises(InvalidFieldValueError):
            attributes.validate_ml_constraints()

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        attr1 = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attr2 = MLAttribute(id="COLOR", name="Color", value_name="Rojo")

        original = MLAttributes(attributes={"BRAND": attr1, "COLOR": attr2})

        # Convert to dict
        data = original.to_dict()

        # Convert back
        restored = MLAttributes.from_dict(data)

        assert original == restored
        assert len(restored.attributes) == 2
        assert restored.has_attribute("BRAND")
        assert restored.has_attribute("COLOR")

    def test_json_serialization(self):
        """Test JSON serialization."""
        attr = MLAttribute(id="BRAND", name="Marca", value_name="Nike")
        attributes = MLAttributes(attributes={"BRAND": attr})

        # To JSON
        json_str = attributes.to_json()

        # From JSON
        restored = MLAttributes.from_json(json_str)

        assert attributes == restored
        assert restored.has_attribute("BRAND")
