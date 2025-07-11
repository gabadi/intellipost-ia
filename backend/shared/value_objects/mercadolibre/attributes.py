"""
MercadoLibre attributes value object.

This module defines the MLAttributes value object for handling
MercadoLibre product attributes in a type-safe manner.
"""

import re
from dataclasses import dataclass
from typing import Any

from shared.value_objects.base import BaseValueObject
from shared.value_objects.exceptions import (
    InvalidFieldFormatError,
    InvalidFieldTypeError,
    InvalidFieldValueError,
    MultipleValidationError,
    RequiredFieldError,
    ValueObjectValidationError,
)


@dataclass(frozen=True)
class MLAttribute:
    """Individual MercadoLibre attribute."""

    id: str
    name: str
    value_id: str | None = None
    value_name: str | None = None
    value_struct: dict[str, Any] | None = None
    values: list[dict[str, Any]] | None = None
    attribute_group_id: str | None = None
    attribute_group_name: str | None = None

    def __post_init__(self):
        """Validate attribute after initialization."""
        if not self.id:
            raise RequiredFieldError("id")
        if not self.name:
            raise RequiredFieldError("name")

        # Validate that we have some form of value
        if not any([self.value_id, self.value_name, self.value_struct, self.values]):
            raise InvalidFieldValueError(
                "attribute_value",
                None,
                "At least one value field (value_id, value_name, value_struct, or values) must be provided",
            )


@dataclass(frozen=True, eq=False)
class MLAttributes(BaseValueObject):
    """
    MercadoLibre attributes value object.

    This value object encapsulates MercadoLibre product attributes,
    providing validation and serialization capabilities.
    """

    attributes: dict[str, MLAttribute]

    def validate(self) -> None:
        """Validate the MLAttributes value object."""
        errors = []

        # Validate attributes dict
        if not isinstance(self.attributes, dict):
            errors.append(InvalidFieldTypeError("attributes", self.attributes, "dict"))
        else:
            # Validate each attribute
            for attr_id, attribute in self.attributes.items():
                try:
                    if not isinstance(attribute, MLAttribute):
                        errors.append(
                            InvalidFieldTypeError(
                                f"attributes[{attr_id}]", attribute, "MLAttribute"
                            )
                        )
                    else:
                        # Validate attribute ID matches key
                        if attribute.id != attr_id:
                            errors.append(
                                InvalidFieldValueError(
                                    f"attributes[{attr_id}].id",
                                    attribute.id,
                                    f"Attribute ID must match dictionary key '{attr_id}'",
                                )
                            )
                except Exception as e:
                    errors.append(
                        ValueObjectValidationError(
                            f"Error validating attribute {attr_id}: {str(e)}",
                            f"attributes[{attr_id}]",
                        )
                    )

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        if field_name == "attributes":
            if not isinstance(field_value, dict):
                raise InvalidFieldTypeError(field_name, field_value, "dict")

            for attr_id, attribute in field_value.items():
                if not isinstance(attribute, MLAttribute):
                    raise InvalidFieldTypeError(
                        f"{field_name}[{attr_id}]", attribute, "MLAttribute"
                    )
        else:
            raise InvalidFieldValueError(
                field_name, field_value, f"Unknown field '{field_name}'"
            )

    def to_ml_api_format(self) -> dict[str, Any]:
        """Convert to MercadoLibre API format."""
        api_attributes = []

        for attribute in self.attributes.values():
            attr_data = {
                "id": attribute.id,
                "name": attribute.name,
            }

            if attribute.value_id:
                attr_data["value_id"] = attribute.value_id
            if attribute.value_name:
                attr_data["value_name"] = attribute.value_name
            if attribute.value_struct:
                attr_data["value_struct"] = attribute.value_struct
            if attribute.values:
                attr_data["values"] = attribute.values
            if attribute.attribute_group_id:
                attr_data["attribute_group_id"] = attribute.attribute_group_id
            if attribute.attribute_group_name:
                attr_data["attribute_group_name"] = attribute.attribute_group_name

            api_attributes.append(attr_data)

        return {"attributes": api_attributes}

    @classmethod
    def from_ml_api_format(cls, data: dict[str, Any]) -> "MLAttributes":
        """Create from MercadoLibre API format."""
        if "attributes" not in data:
            raise InvalidFieldValueError(
                "attributes", None, "Missing 'attributes' field in API data"
            )

        attributes = {}

        for attr_data in data["attributes"]:
            if not isinstance(attr_data, dict):
                raise InvalidFieldTypeError("attribute", attr_data, "dict")

            if "id" not in attr_data:
                raise RequiredFieldError("id")
            if "name" not in attr_data:
                raise RequiredFieldError("name")

            attr_id = attr_data["id"]
            attribute = MLAttribute(
                id=attr_id,
                name=attr_data["name"],
                value_id=attr_data.get("value_id"),
                value_name=attr_data.get("value_name"),
                value_struct=attr_data.get("value_struct"),
                values=attr_data.get("values"),
                attribute_group_id=attr_data.get("attribute_group_id"),
                attribute_group_name=attr_data.get("attribute_group_name"),
            )

            attributes[attr_id] = attribute

        return cls(attributes=attributes)

    def validate_ml_constraints(self) -> None:
        """Validate MercadoLibre-specific constraints."""
        errors = []

        # Validate each attribute follows ML constraints
        for attr_id, attribute in self.attributes.items():
            # Validate attribute ID format (ML uses specific patterns)
            if not re.match(r"^[A-Z_][A-Z0-9_]*$", attribute.id):
                errors.append(
                    InvalidFieldFormatError(
                        f"attributes[{attr_id}].id",
                        attribute.id,
                        "MercadoLibre attribute IDs must be uppercase letters, numbers, and underscores",
                    )
                )

            # Validate attribute name length
            if len(attribute.name) > 255:
                errors.append(
                    InvalidFieldValueError(
                        f"attributes[{attr_id}].name",
                        attribute.name,
                        "Attribute name must be 255 characters or less",
                    )
                )

            # Validate value_name length if present
            if attribute.value_name and len(attribute.value_name) > 255:
                errors.append(
                    InvalidFieldValueError(
                        f"attributes[{attr_id}].value_name",
                        attribute.value_name,
                        "Attribute value name must be 255 characters or less",
                    )
                )

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise MultipleValidationError(errors)

    def get_attribute(self, attribute_id: str) -> MLAttribute | None:
        """Get a specific attribute by ID."""
        return self.attributes.get(attribute_id)

    def has_attribute(self, attribute_id: str) -> bool:
        """Check if an attribute exists."""
        return attribute_id in self.attributes

    def get_attribute_value(self, attribute_id: str) -> Any:
        """Get the value of a specific attribute."""
        attribute = self.get_attribute(attribute_id)
        if not attribute:
            return None

        # Return the most appropriate value
        if attribute.value_struct:
            return attribute.value_struct
        elif attribute.values:
            return attribute.values
        elif attribute.value_name:
            return attribute.value_name
        elif attribute.value_id:
            return attribute.value_id
        else:
            return None

    def add_attribute(self, attribute: MLAttribute) -> "MLAttributes":
        """Add or update an attribute, returning a new instance."""
        new_attributes = self.attributes.copy()
        new_attributes[attribute.id] = attribute
        return MLAttributes(attributes=new_attributes)

    def remove_attribute(self, attribute_id: str) -> "MLAttributes":
        """Remove an attribute, returning a new instance."""
        if attribute_id not in self.attributes:
            return self

        new_attributes = self.attributes.copy()
        del new_attributes[attribute_id]
        return MLAttributes(attributes=new_attributes)

    def get_attribute_count(self) -> int:
        """Get the number of attributes."""
        return len(self.attributes)

    def is_empty(self) -> bool:
        """Check if there are no attributes."""
        return len(self.attributes) == 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MLAttributes":
        """
        Create from dictionary, handling nested MLAttribute objects.

        Args:
            data: Dictionary containing the value object data.

        Returns:
            New instance of the value object.
        """
        try:
            if "attributes" in data:
                attributes = {}
                for attr_id, attr_data in data["attributes"].items():
                    if isinstance(attr_data, dict):
                        attribute = MLAttribute(**attr_data)
                    else:
                        attribute = attr_data  # Already an MLAttribute
                    attributes[attr_id] = attribute

                return cls(attributes=attributes)
            else:
                return super().from_dict(data)  # type: ignore
        except Exception:
            return super().from_dict(data)  # type: ignore

    @classmethod
    def empty(cls) -> "MLAttributes":
        """Create an empty MLAttributes instance."""
        return cls(attributes={})
