"""
Tests for base value object implementation.
"""

import json
from dataclasses import dataclass
from typing import Any

import pytest

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import (
    InvalidFieldTypeError,
    RequiredFieldError,
    ValueObjectDeserializationError,
    ValueObjectValidationError,
)

pytestmark = pytest.mark.unit


@dataclass(frozen=True, eq=False)
class TestValueObject(BaseValueObject):
    """Test value object for testing purposes."""

    name: str
    value: int
    optional_field: str | None = None

    def validate(self) -> None:
        """Validate the test value object."""
        if not self.name:
            raise RequiredFieldError("name")
        if not isinstance(self.value, int):
            raise InvalidFieldTypeError("value", self.value, "int")
        if self.value < 0:
            raise ValueObjectValidationError(
                "Value must be non-negative", "value", self.value
            )

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        if field_name == "name":
            if not field_value:
                raise RequiredFieldError("name")
        elif field_name == "value":
            if not isinstance(field_value, int):
                raise InvalidFieldTypeError("value", field_value, "int")
            if field_value < 0:
                raise ValueObjectValidationError(
                    "Value must be non-negative", "value", field_value
                )
        elif field_name == "optional_field":
            if field_value is not None and not isinstance(field_value, str):
                raise InvalidFieldTypeError("optional_field", field_value, "str")


class TestBaseValueObject:
    """Test cases for BaseValueObject."""

    def test_valid_value_object_creation(self):
        """Test creating a valid value object."""
        obj = TestValueObject(name="test", value=42, optional_field="optional")

        assert obj.name == "test"
        assert obj.value == 42
        assert obj.optional_field == "optional"
        assert obj.is_valid()

    def test_value_object_with_none_optional_field(self):
        """Test creating a value object with None optional field."""
        obj = TestValueObject(name="test", value=42)

        assert obj.name == "test"
        assert obj.value == 42
        assert obj.optional_field is None
        assert obj.is_valid()

    def test_validation_on_creation(self):
        """Test that validation is called during creation."""
        with pytest.raises(RequiredFieldError):
            TestValueObject(name="", value=42)

        with pytest.raises(InvalidFieldTypeError):
            TestValueObject(name="test", value="not an int")

        with pytest.raises(ValueObjectValidationError):
            TestValueObject(name="test", value=-1)

    def test_validation_disabled(self):
        """Test creating value object with validation disabled."""

        # Create a test class with validation disabled
        @dataclass(frozen=True)
        class TestObjectNoValidation(BaseValueObject):
            name: str
            value: int
            _validation_enabled = False

            def validate(self) -> None:
                if not self.name:
                    raise RequiredFieldError("name")

            def validate_field(self, field_name: str, field_value: Any) -> None:
                pass

        # This should not raise an error even with invalid data
        obj = TestObjectNoValidation(name="", value=42)
        assert obj.name == ""
        assert not obj.is_valid()

    def test_to_dict(self):
        """Test converting value object to dictionary."""
        obj = TestValueObject(name="test", value=42, optional_field="optional")
        result = obj.to_dict()

        expected = {"name": "test", "value": 42, "optional_field": "optional"}
        assert result == expected

    def test_from_dict(self):
        """Test creating value object from dictionary."""
        data = {"name": "test", "value": 42, "optional_field": "optional"}
        obj = TestValueObject.from_dict(data)

        assert obj.name == "test"
        assert obj.value == 42
        assert obj.optional_field == "optional"

    def test_from_dict_with_extra_fields(self):
        """Test creating value object from dictionary with extra fields."""
        data = {
            "name": "test",
            "value": 42,
            "optional_field": "optional",
            "extra_field": "ignored",
        }
        obj = TestValueObject.from_dict(data)

        assert obj.name == "test"
        assert obj.value == 42
        assert obj.optional_field == "optional"
        assert not hasattr(obj, "extra_field")

    def test_from_dict_with_invalid_data(self):
        """Test creating value object from invalid dictionary."""
        with pytest.raises(ValueObjectDeserializationError):
            TestValueObject.from_dict({"name": "test"})  # Missing required field

    def test_to_json(self):
        """Test converting value object to JSON."""
        obj = TestValueObject(name="test", value=42, optional_field="optional")
        result = obj.to_json()

        expected_data = {"name": "test", "value": 42, "optional_field": "optional"}
        assert json.loads(result) == expected_data

    def test_from_json(self):
        """Test creating value object from JSON."""
        json_data = '{"name": "test", "value": 42, "optional_field": "optional"}'
        obj = TestValueObject.from_json(json_data)

        assert obj.name == "test"
        assert obj.value == 42
        assert obj.optional_field == "optional"

    def test_from_json_invalid_json(self):
        """Test creating value object from invalid JSON."""
        with pytest.raises(ValueObjectDeserializationError):
            TestValueObject.from_json("invalid json")

    def test_from_json_non_dict(self):
        """Test creating value object from JSON that's not a dict."""
        with pytest.raises(ValueObjectDeserializationError):
            TestValueObject.from_json('"not a dict"')

    def test_equality(self):
        """Test value object equality."""
        obj1 = TestValueObject(name="test", value=42, optional_field="optional")
        obj2 = TestValueObject(name="test", value=42, optional_field="optional")
        obj3 = TestValueObject(name="test", value=43, optional_field="optional")

        assert obj1 == obj2
        assert obj1 != obj3
        assert obj1 != "not a value object"

    def test_hash(self):
        """Test value object hashing."""
        obj1 = TestValueObject(name="test", value=42, optional_field="optional")
        obj2 = TestValueObject(name="test", value=42, optional_field="optional")
        obj3 = TestValueObject(name="test", value=43, optional_field="optional")

        assert hash(obj1) == hash(obj2)
        assert hash(obj1) != hash(obj3)

        # Test that objects can be used in sets
        obj_set = {obj1, obj2, obj3}
        assert len(obj_set) == 2  # obj1 and obj2 are equal

    def test_hash_with_mutable_fields(self):
        """Test hashing with mutable field types."""

        @dataclass(frozen=True, eq=False)
        class TestObjectWithList(BaseValueObject):
            name: str
            items: list[str]

            def validate(self) -> None:
                pass

            def validate_field(self, field_name: str, field_value: Any) -> None:
                pass

        obj1 = TestObjectWithList(name="test", items=["a", "b"])
        obj2 = TestObjectWithList(name="test", items=["a", "b"])

        # These should work with our custom hash implementation
        assert hash(obj1) == hash(obj2)
        assert obj1 == obj2

        # Test with lists containing unhashable items
        @dataclass(frozen=True, eq=False)
        class TestObjectWithComplexList(BaseValueObject):
            name: str
            items: list[dict[str, Any]]

            def validate(self) -> None:
                pass

            def validate_field(self, field_name: str, field_value: Any) -> None:
                pass

        complex_obj1 = TestObjectWithComplexList(
            name="test", items=[{"a": 1}, {"b": 2}]
        )
        complex_obj2 = TestObjectWithComplexList(
            name="test", items=[{"a": 1}, {"b": 2}]
        )

        # Should work with string representation fallback
        assert hash(complex_obj1) == hash(complex_obj2)
        assert complex_obj1 == complex_obj2

    def test_str_representation(self):
        """Test string representation of value object."""
        obj = TestValueObject(name="test", value=42, optional_field="optional")
        str_repr = str(obj)

        assert "TestValueObject" in str_repr
        assert "test" in str_repr
        assert "42" in str_repr

    def test_repr_representation(self):
        """Test repr representation of value object."""
        obj = TestValueObject(name="test", value=42, optional_field="optional")
        repr_str = repr(obj)

        assert "TestValueObject" in repr_str
        assert "test" in repr_str
        assert "42" in repr_str

    def test_get_validation_errors(self):
        """Test getting validation errors without raising exceptions."""
        obj = TestValueObject(name="test", value=42)
        errors = obj.get_validation_errors()
        assert len(errors) == 0

        # Test with invalid object (created with validation disabled)
        @dataclass(frozen=True)
        class InvalidTestObject(BaseValueObject):
            name: str
            value: int
            _validation_enabled = False

            def validate(self) -> None:
                if not self.name:
                    raise RequiredFieldError("name")
                if self.value < 0:
                    raise ValueObjectValidationError(
                        "Value must be non-negative", "value", self.value
                    )

            def validate_field(self, field_name: str, field_value: Any) -> None:
                pass

        invalid_obj = InvalidTestObject(name="", value=-1)
        errors = invalid_obj.get_validation_errors()
        assert len(errors) == 1
        assert "name" in errors[0]

    def test_is_valid(self):
        """Test checking if value object is valid."""
        valid_obj = TestValueObject(name="test", value=42)
        assert valid_obj.is_valid()

        # Create invalid object with validation disabled
        @dataclass(frozen=True)
        class InvalidTestObject(BaseValueObject):
            name: str
            _validation_enabled = False

            def validate(self) -> None:
                if not self.name:
                    raise RequiredFieldError("name")

            def validate_field(self, field_name: str, field_value: Any) -> None:
                pass

        invalid_obj = InvalidTestObject(name="")
        assert not invalid_obj.is_valid()

    def test_nested_value_objects(self):
        """Test value objects with nested value objects."""

        @dataclass(frozen=True)
        class NestedValueObject(BaseValueObject):
            inner: TestValueObject
            name: str

            def validate(self) -> None:
                if not self.name:
                    raise RequiredFieldError("name")

            def validate_field(self, field_name: str, field_value: Any) -> None:
                if field_name == "name" and not field_value:
                    raise RequiredFieldError("name")

        inner_obj = TestValueObject(name="inner", value=42)
        nested_obj = NestedValueObject(inner=inner_obj, name="nested")

        # Test to_dict handles nested objects
        result = nested_obj.to_dict()
        expected = {
            "inner": {"name": "inner", "value": 42, "optional_field": None},
            "name": "nested",
        }
        assert result == expected

        # Test equality with nested objects
        inner_obj2 = TestValueObject(name="inner", value=42)
        nested_obj2 = NestedValueObject(inner=inner_obj2, name="nested")
        assert nested_obj == nested_obj2

    def test_with_list_of_value_objects(self):
        """Test value objects with lists of value objects."""

        @dataclass(frozen=True)
        class ListValueObject(BaseValueObject):
            items: list[TestValueObject]
            name: str

            def validate(self) -> None:
                if not self.name:
                    raise RequiredFieldError("name")

            def validate_field(self, field_name: str, field_value: Any) -> None:
                if field_name == "name" and not field_value:
                    raise RequiredFieldError("name")

        item1 = TestValueObject(name="item1", value=1)
        item2 = TestValueObject(name="item2", value=2)
        list_obj = ListValueObject(items=[item1, item2], name="list")

        # Test to_dict handles lists of objects
        result = list_obj.to_dict()
        expected = {
            "items": [
                {"name": "item1", "value": 1, "optional_field": None},
                {"name": "item2", "value": 2, "optional_field": None},
            ],
            "name": "list",
        }
        assert result == expected
