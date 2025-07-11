"""
Base value object implementation for Domain-Driven Design.

Provides immutable value objects with validation, serialization, and equality.
All value objects should inherit from BaseValueObject and implement validate().
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from .exceptions import (
    MultipleValidationError,
    ValueObjectDeserializationError,
    ValueObjectError,
    ValueObjectSerializationError,
    ValueObjectValidationError,
)


@dataclass(frozen=True, eq=False)
class BaseValueObject(ABC):
    """Abstract base class for all value objects with validation and serialization."""

    # Class-level configuration
    _validation_enabled: ClassVar[bool] = True
    _strict_validation: ClassVar[bool] = True

    def __post_init__(self):
        if self._validation_enabled:
            self.validate()

    @abstractmethod
    def validate(self) -> None:
        """Validate the value object's data. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        pass

    def get_validation_errors(self) -> list[str]:
        """Get validation errors without raising exceptions."""
        errors = []

        try:
            self.validate()
        except ValueObjectValidationError as e:
            errors.append(str(e))
        except MultipleValidationError as e:
            errors.extend(str(error) for error in e.errors)
        except Exception as e:
            errors.append(f"Unexpected validation error: {str(e)}")

        return errors

    def is_valid(self) -> bool:
        """Check if the value object is valid."""
        return len(self.get_validation_errors()) == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {}

        # Get all fields from the dataclass, excluding class variables
        for field_name in self.__dataclass_fields__:
            if field_name.startswith("_"):
                continue
            field_value = getattr(self, field_name)

            # Handle nested value objects
            if isinstance(field_value, BaseValueObject):
                result[field_name] = field_value.to_dict()
            # Handle lists of value objects
            elif isinstance(field_value, list):
                result[field_name] = [
                    item.to_dict() if isinstance(item, BaseValueObject) else item
                    for item in field_value
                ]
            # Handle dictionaries with value objects (like in ML classes)
            elif isinstance(field_value, dict):
                converted_dict = {}
                for key, value in field_value.items():
                    if hasattr(
                        value, "__dataclass_fields__"
                    ):  # Check if it's a dataclass
                        # Convert dataclass to dict representation
                        converted_dict[key] = {
                            field: getattr(value, field)
                            for field in value.__dataclass_fields__
                            if not field.startswith("_")
                        }
                    elif isinstance(value, BaseValueObject):
                        converted_dict[key] = value.to_dict()
                    else:
                        converted_dict[key] = value
                result[field_name] = converted_dict
            else:
                result[field_name] = field_value

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseValueObject":
        """Create value object from dictionary."""
        try:
            # Filter data to only include fields that exist in the dataclass
            filtered_data = {
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }

            return cls(**filtered_data)

        except Exception as e:
            raise ValueObjectDeserializationError(
                f"Failed to deserialize {cls.__name__} from dictionary",
                input_data=data,
                expected_type=cls.__name__,
                original_error=e,
            ) from e

    def to_json(self) -> str:
        """Convert to JSON string."""
        try:
            return json.dumps(self.to_dict(), default=str, ensure_ascii=False)
        except Exception as e:
            raise ValueObjectSerializationError(
                f"Failed to serialize {self.__class__.__name__} to JSON",
                serialization_format="json",
                original_error=e,
            ) from e

    @classmethod
    def from_json(cls, json_str: str) -> "BaseValueObject":
        """Create value object from JSON string."""
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise ValueError("JSON must represent a dictionary")
            return cls.from_dict(data)
        except Exception as e:
            raise ValueObjectDeserializationError(
                f"Failed to deserialize {cls.__name__} from JSON",
                input_data=json_str,
                expected_type=cls.__name__,
                original_error=e,
            ) from e

    def __eq__(self, other: Any) -> bool:
        """Check equality with another value object."""
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        """Calculate hash of the value object."""
        # Create hash from all field values
        values = []
        for field_name in sorted(self.__dataclass_fields__.keys()):
            if field_name.startswith("_"):
                continue
            field_value = getattr(self, field_name)

            # Convert value to hashable representation
            hashable_value = self._make_hashable(field_value)
            values.append(hashable_value)

        return hash(tuple(values))

    def _make_hashable(self, value: Any) -> Any:
        """Convert a value to a hashable representation."""
        if isinstance(value, list):
            # Handle lists that may contain unhashable items
            try:
                return tuple(self._make_hashable(item) for item in value)
            except TypeError:
                # If items are not hashable, convert to string representation
                return tuple(str(item) for item in value)
        elif isinstance(value, dict):
            # Convert dict to sorted tuple of items
            try:
                return tuple(
                    sorted((k, self._make_hashable(v)) for k, v in value.items())
                )
            except TypeError:
                # If items are not hashable, convert to string representation
                return tuple(sorted((k, str(v)) for k, v in value.items()))
        elif isinstance(value, BaseValueObject):
            # Use the value object's hash
            return hash(value)
        elif hasattr(value, "__dataclass_fields__"):
            # Handle other dataclasses by converting to string
            return str(value)
        else:
            # Return the value as-is (should be hashable)
            return value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"

    def __repr__(self) -> str:
        return self.__str__()


# Export the exception for convenience
__all__ = ["BaseValueObject", "ValueObjectError"]
