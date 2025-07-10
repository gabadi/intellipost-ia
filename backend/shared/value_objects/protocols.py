"""
Value object protocols for type safety.

This module defines protocol interfaces that value objects must implement
to ensure consistent behavior across the application.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ValueObjectProtocol(Protocol):
    """Protocol that all value objects must implement."""

    def validate(self) -> None:
        """
        Validate the value object's data.

        Raises:
            ValueObjectValidationError: If validation fails.
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the value object to a dictionary representation.

        Returns:
            Dictionary representation of the value object.
        """
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValueObjectProtocol":
        """
        Create a value object from a dictionary.

        Args:
            data: Dictionary containing the value object data.

        Returns:
            New instance of the value object.

        Raises:
            ValueObjectDeserializationError: If deserialization fails.
        """
        ...

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another value object.

        Args:
            other: Object to compare with.

        Returns:
            True if objects are equal, False otherwise.
        """
        ...

    def __hash__(self) -> int:
        """
        Calculate hash of the value object.

        Returns:
            Hash value.
        """
        ...


@runtime_checkable
class SerializableValueObjectProtocol(ValueObjectProtocol, Protocol):
    """Protocol for value objects that support serialization."""

    def to_json(self) -> str:
        """
        Convert the value object to JSON string.

        Returns:
            JSON string representation.

        Raises:
            ValueObjectSerializationError: If serialization fails.
        """
        ...

    @classmethod
    def from_json(cls, json_str: str) -> "SerializableValueObjectProtocol":
        """
        Create a value object from JSON string.

        Args:
            json_str: JSON string containing the value object data.

        Returns:
            New instance of the value object.

        Raises:
            ValueObjectDeserializationError: If deserialization fails.
        """
        ...


@runtime_checkable
class ValidatedValueObjectProtocol(ValueObjectProtocol, Protocol):
    """Protocol for value objects with enhanced validation."""

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """
        Validate a specific field.

        Args:
            field_name: Name of the field to validate.
            field_value: Value of the field to validate.

        Raises:
            ValueObjectValidationError: If field validation fails.
        """
        ...

    def get_validation_errors(self) -> list[str]:
        """
        Get list of all validation errors without raising exceptions.

        Returns:
            List of validation error messages.
        """
        ...

    def is_valid(self) -> bool:
        """
        Check if the value object is valid.

        Returns:
            True if valid, False otherwise.
        """
        ...


@runtime_checkable
class MercadoLibreValueObjectProtocol(ValueObjectProtocol, Protocol):
    """Protocol for MercadoLibre-specific value objects."""

    def to_ml_api_format(self) -> dict[str, Any]:
        """
        Convert to MercadoLibre API format.

        Returns:
            Dictionary in MercadoLibre API format.
        """
        ...

    @classmethod
    def from_ml_api_format(
        cls, data: dict[str, Any]
    ) -> "MercadoLibreValueObjectProtocol":
        """
        Create from MercadoLibre API format.

        Args:
            data: Dictionary in MercadoLibre API format.

        Returns:
            New instance of the value object.
        """
        ...

    def validate_ml_constraints(self) -> None:
        """
        Validate MercadoLibre-specific constraints.

        Raises:
            ValueObjectValidationError: If ML validation fails.
        """
        ...
