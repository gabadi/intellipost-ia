"""
Value object protocols for type safety and duck typing.

This module defines protocol interfaces that value objects must implement
to ensure consistent behavior across the application. These protocols enable
duck typing patterns, allowing any class that implements the required methods
to be used as a value object without explicit inheritance.

## Duck Typing Benefits:

1. **Flexibility**: Classes can implement protocols without explicit inheritance
2. **Testability**: Easy to create mock objects for testing
3. **Loose Coupling**: Reduces dependencies between components
4. **Runtime Checking**: @runtime_checkable allows isinstance() checks

## Usage Examples:

### Basic Protocol Implementation (Duck Typing):
```python
from shared.value_objects.protocols import ValueObjectProtocol

class CustomValue:  # No explicit inheritance needed
    def __init__(self, value: str):
        self.value = value

    def validate(self) -> None:
        if not self.value:
            raise ValueError("Value cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CustomValue":
        return cls(data["value"])

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CustomValue) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

# This works due to duck typing - no inheritance required!
def process_value_object(vo: ValueObjectProtocol) -> dict[str, Any]:
    vo.validate()
    return vo.to_dict()

custom = CustomValue("test")
result = process_value_object(custom)  # Works perfectly!
```

### Runtime Type Checking:
```python
from shared.value_objects.protocols import ValueObjectProtocol

# Runtime check without inheritance
assert isinstance(custom, ValueObjectProtocol)  # True!
```

### Mock Objects for Testing:
```python
class MockValueObject:
    def validate(self) -> None: pass
    def to_dict(self) -> dict[str, Any]: return {}
    @classmethod
    def from_dict(cls, data: dict[str, Any]): return cls()
    def __eq__(self, other: Any) -> bool: return True
    def __hash__(self) -> int: return 0

# Mock works seamlessly with protocol-typed functions
mock = MockValueObject()
result = process_value_object(mock)  # No inheritance needed!
```
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ValueObjectProtocol(Protocol):
    """
    Protocol that all value objects must implement.

    This protocol defines the minimum interface that any value object
    must provide. Classes implementing this protocol can be used anywhere
    a ValueObjectProtocol is expected, without explicit inheritance.

    Example Implementation:
    ```python
    class EmailAddress:  # No inheritance from BaseValueObject
        def __init__(self, email: str):
            self.email = email

        def validate(self) -> None:
            if "@" not in self.email:
                raise ValueError("Invalid email format")

        def to_dict(self) -> dict[str, Any]:
            return {"email": self.email}

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "EmailAddress":
            return cls(data["email"])

        def __eq__(self, other: Any) -> bool:
            return isinstance(other, EmailAddress) and self.email == other.email

        def __hash__(self) -> int:
            return hash(self.email)

    # Usage with duck typing
    def store_contact(vo: ValueObjectProtocol) -> None:
        vo.validate()  # Ensures data is valid
        data = vo.to_dict()  # Gets serializable representation
        # ... store to database

    email = EmailAddress("user@example.com")
    store_contact(email)  # Works without inheritance!
    ```
    """

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
    """
    Protocol for value objects that support JSON serialization.

    Extends ValueObjectProtocol with JSON serialization capabilities.
    Perfect for API responses and data persistence scenarios.

    Example Implementation:
    ```python
    import json

    class ProductPrice:  # No inheritance needed
        def __init__(self, amount: float, currency: str):
            self.amount = amount
            self.currency = currency

        def validate(self) -> None:
            if self.amount < 0:
                raise ValueError("Price cannot be negative")
            if not self.currency:
                raise ValueError("Currency is required")

        def to_dict(self) -> dict[str, Any]:
            return {"amount": self.amount, "currency": self.currency}

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "ProductPrice":
            return cls(data["amount"], data["currency"])

        def to_json(self) -> str:
            return json.dumps(self.to_dict())

        @classmethod
        def from_json(cls, json_str: str) -> "ProductPrice":
            data = json.loads(json_str)
            return cls.from_dict(data)

        def __eq__(self, other: Any) -> bool:
            return (isinstance(other, ProductPrice) and
                   self.amount == other.amount and
                   self.currency == other.currency)

        def __hash__(self) -> int:
            return hash((self.amount, self.currency))

    # Usage in API layer
    def serialize_for_api(vo: SerializableValueObjectProtocol) -> str:
        vo.validate()
        return vo.to_json()  # Direct JSON serialization

    price = ProductPrice(99.99, "USD")
    json_data = serialize_for_api(price)  # Works with duck typing!
    ```
    """

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
