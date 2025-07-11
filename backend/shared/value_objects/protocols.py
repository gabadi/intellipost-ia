"""
Value object protocols for type safety and duck typing.

Defines protocol interfaces for value objects, enabling duck typing patterns
without explicit inheritance.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ValueObjectProtocol(Protocol):
    """Protocol that all value objects must implement."""

    def validate(self) -> None:
        """Validate the value object's data."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValueObjectProtocol":
        """Create value object from dictionary."""
        ...

    def __eq__(self, other: Any) -> bool:
        """Check equality with another value object."""
        ...

    def __hash__(self) -> int:
        """Calculate hash of the value object."""
        ...


@runtime_checkable
class SerializableValueObjectProtocol(ValueObjectProtocol, Protocol):
    """Protocol for value objects with JSON serialization support."""

    def to_json(self) -> str:
        """Convert to JSON string."""
        ...

    @classmethod
    def from_json(cls, json_str: str) -> "SerializableValueObjectProtocol":
        """Create value object from JSON string."""
        ...


@runtime_checkable
class ValidatedValueObjectProtocol(ValueObjectProtocol, Protocol):
    """Protocol for value objects with enhanced validation."""

    def validate_field(self, field_name: str, field_value: Any) -> None:
        """Validate a specific field."""
        ...

    def get_validation_errors(self) -> list[str]:
        """Get validation errors without raising exceptions."""
        ...

    def is_valid(self) -> bool:
        """Check if the value object is valid."""
        ...


@runtime_checkable
class MercadoLibreValueObjectProtocol(ValueObjectProtocol, Protocol):
    """Protocol for MercadoLibre-specific value objects."""

    def to_ml_api_format(self) -> dict[str, Any]:
        """Convert to MercadoLibre API format."""
        ...

    @classmethod
    def from_ml_api_format(
        cls, data: dict[str, Any]
    ) -> "MercadoLibreValueObjectProtocol":
        """Create from MercadoLibre API format."""
        ...

    def validate_ml_constraints(self) -> None:
        """Validate MercadoLibre-specific constraints."""
        ...
