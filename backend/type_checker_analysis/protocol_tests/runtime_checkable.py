"""
Test cases for runtime_checkable protocol behavior.

This module tests whether type checkers correctly handle runtime_checkable
protocols and their behavior with isinstance checks.
"""

from typing import Protocol, runtime_checkable, Any, Union
from uuid import UUID


@runtime_checkable
class DrawableProtocol(Protocol):
    """Runtime checkable protocol for drawable objects."""

    def draw(self) -> None:
        """Draw the object."""
        ...

    def get_bounds(self) -> tuple[int, int, int, int]:
        """Get bounding box as (x, y, width, height)."""
        ...


@runtime_checkable
class SerializableProtocol(Protocol):
    """Runtime checkable protocol for serializable objects."""

    def serialize(self) -> dict[str, Any]:
        """Serialize object to dictionary."""
        ...

    def deserialize(self, data: dict[str, Any]) -> None:
        """Deserialize object from dictionary."""
        ...


@runtime_checkable
class ConfigurableProtocol(Protocol):
    """Runtime checkable protocol for configurable objects."""

    def configure(self, config: dict[str, Any]) -> None:
        """Configure object with settings."""
        ...

    def get_config(self) -> dict[str, Any]:
        """Get current configuration."""
        ...


class Circle:
    """Circle class that implements DrawableProtocol."""

    def __init__(self, x: int, y: int, radius: int):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self) -> None:
        print(f"Drawing circle at ({self.x}, {self.y}) with radius {self.radius}")

    def get_bounds(self) -> tuple[int, int, int, int]:
        return (self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)


class Rectangle:
    """Rectangle class that implements DrawableProtocol."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self) -> None:
        print(f"Drawing rectangle at ({self.x}, {self.y}) with size {self.width}x{self.height}")

    def get_bounds(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


class IncompleteShape:
    """Shape that doesn't fully implement DrawableProtocol."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def draw(self) -> None:
        print(f"Drawing shape at ({self.x}, {self.y})")

    # Missing: get_bounds method


class User:
    """User class that implements SerializableProtocol."""

    def __init__(self, user_id: UUID, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def serialize(self) -> dict[str, Any]:
        return {
            "user_id": str(self.user_id),
            "name": self.name,
            "email": self.email
        }

    def deserialize(self, data: dict[str, Any]) -> None:
        self.user_id = UUID(data["user_id"])
        self.name = data["name"]
        self.email = data["email"]


class DatabaseConnection:
    """Database connection that implements ConfigurableProtocol."""

    def __init__(self):
        self.config = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "timeout": 30
        }

    def configure(self, config: dict[str, Any]) -> None:
        self.config.update(config)

    def get_config(self) -> dict[str, Any]:
        return self.config.copy()


class NonSerializableObject:
    """Object that doesn't implement SerializableProtocol."""

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return self.value


class ConfigurableDrawable:
    """Object that implements multiple protocols."""

    def __init__(self, name: str):
        self.name = name
        self.config = {"visible": True, "color": "black"}

    def draw(self) -> None:
        if self.config.get("visible", True):
            print(f"Drawing {self.name} in {self.config.get('color', 'black')}")

    def get_bounds(self) -> tuple[int, int, int, int]:
        return (0, 0, 100, 100)

    def configure(self, config: dict[str, Any]) -> None:
        self.config.update(config)

    def get_config(self) -> dict[str, Any]:
        return self.config.copy()


# Test functions
def draw_object(obj: DrawableProtocol) -> None:
    """Draw an object that implements DrawableProtocol."""
    obj.draw()
    bounds = obj.get_bounds()
    print(f"Object bounds: {bounds}")


def serialize_object(obj: SerializableProtocol) -> dict[str, Any]:
    """Serialize an object that implements SerializableProtocol."""
    return obj.serialize()


def configure_object(obj: ConfigurableProtocol, config: dict[str, Any]) -> dict[str, Any]:
    """Configure an object that implements ConfigurableProtocol."""
    obj.configure(config)
    return obj.get_config()


def test_runtime_checkable():
    """Test runtime_checkable protocol behavior."""

    # Create test objects
    circle = Circle(10, 20, 5)
    rectangle = Rectangle(0, 0, 100, 50)
    incomplete_shape = IncompleteShape(5, 5)
    user = User(UUID("123e4567-e89b-12d3-a456-426614174000"), "John Doe", "john@example.com")
    db_conn = DatabaseConnection()
    non_serializable = NonSerializableObject("test")
    configurable_drawable = ConfigurableDrawable("test_shape")

    # Test isinstance checks - these should work at runtime
    print("Runtime isinstance checks:")
    print(f"circle isinstance DrawableProtocol: {isinstance(circle, DrawableProtocol)}")
    print(f"rectangle isinstance DrawableProtocol: {isinstance(rectangle, DrawableProtocol)}")
    print(f"incomplete_shape isinstance DrawableProtocol: {isinstance(incomplete_shape, DrawableProtocol)}")
    print(f"user isinstance SerializableProtocol: {isinstance(user, SerializableProtocol)}")
    print(f"db_conn isinstance ConfigurableProtocol: {isinstance(db_conn, ConfigurableProtocol)}")
    print(f"non_serializable isinstance SerializableProtocol: {isinstance(non_serializable, SerializableProtocol)}")
    print(f"configurable_drawable isinstance DrawableProtocol: {isinstance(configurable_drawable, DrawableProtocol)}")
    print(f"configurable_drawable isinstance ConfigurableProtocol: {isinstance(configurable_drawable, ConfigurableProtocol)}")

    # Test protocol usage - these should be caught by type checkers
    print("\nProtocol usage tests:")

    # These should work
    draw_object(circle)                    # Should be OK
    draw_object(rectangle)                 # Should be OK
    draw_object(configurable_drawable)     # Should be OK

    user_data = serialize_object(user)     # Should be OK

    db_config = configure_object(db_conn, {"timeout": 60})  # Should be OK
    shape_config = configure_object(configurable_drawable, {"color": "red"})  # Should be OK

    # These should fail at type check time
    draw_object(incomplete_shape)          # Should cause error: missing get_bounds
    draw_object(user)                      # Should cause error: doesn't implement DrawableProtocol

    serialize_object(circle)               # Should cause error: doesn't implement SerializableProtocol
    serialize_object(non_serializable)     # Should cause error: doesn't implement SerializableProtocol

    configure_object(circle, {"color": "blue"})  # Should cause error: doesn't implement ConfigurableProtocol
    configure_object(user, {"active": True})     # Should cause error: doesn't implement ConfigurableProtocol


def test_dynamic_protocol_checking():
    """Test dynamic protocol checking scenarios."""

    objects = [
        Circle(0, 0, 10),
        Rectangle(0, 0, 20, 30),
        IncompleteShape(5, 5),
        User(UUID("123e4567-e89b-12d3-a456-426614174000"), "Jane", "jane@example.com"),
        DatabaseConnection(),
        NonSerializableObject("test"),
        ConfigurableDrawable("dynamic_test")
    ]

    print("\nDynamic protocol checking:")

    for i, obj in enumerate(objects):
        print(f"\nObject {i}: {type(obj).__name__}")

        # Check if object implements DrawableProtocol
        if isinstance(obj, DrawableProtocol):
            print("  - Implements DrawableProtocol")
            try:
                draw_object(obj)  # This should work at runtime if isinstance returns True
            except Exception as e:
                print(f"  - Error drawing: {e}")
        else:
            print("  - Does NOT implement DrawableProtocol")
            # This should cause type error but might work at runtime
            try:
                draw_object(obj)  # Type checker should flag this
            except Exception as e:
                print(f"  - Error drawing: {e}")

        # Check if object implements SerializableProtocol
        if isinstance(obj, SerializableProtocol):
            print("  - Implements SerializableProtocol")
            try:
                data = serialize_object(obj)  # This should work at runtime if isinstance returns True
                print(f"  - Serialized: {data}")
            except Exception as e:
                print(f"  - Error serializing: {e}")
        else:
            print("  - Does NOT implement SerializableProtocol")

        # Check if object implements ConfigurableProtocol
        if isinstance(obj, ConfigurableProtocol):
            print("  - Implements ConfigurableProtocol")
            try:
                config = configure_object(obj, {"test": "value"})  # This should work at runtime if isinstance returns True
                print(f"  - Configured: {config}")
            except Exception as e:
                print(f"  - Error configuring: {e}")
        else:
            print("  - Does NOT implement ConfigurableProtocol")


def test_protocol_combinations():
    """Test objects that implement multiple protocols."""

    multi_protocol_obj = ConfigurableDrawable("multi_test")

    # Test that object can be used with multiple protocols
    print("\nMulti-protocol object tests:")

    # Should work - object implements both protocols
    draw_object(multi_protocol_obj)
    configure_object(multi_protocol_obj, {"visible": False})

    # Should fail - object doesn't implement SerializableProtocol
    serialize_object(multi_protocol_obj)  # Should cause type error


def test_union_protocols():
    """Test union of protocols."""

    def process_drawable_or_serializable(obj: Union[DrawableProtocol, SerializableProtocol]) -> str:
        """Process object that implements either DrawableProtocol or SerializableProtocol."""
        if isinstance(obj, DrawableProtocol):
            obj.draw()
            return "drew object"
        elif isinstance(obj, SerializableProtocol):
            data = obj.serialize()
            return f"serialized object: {data}"
        else:
            return "unknown object type"

    print("\nUnion protocol tests:")

    circle = Circle(0, 0, 5)
    user = User(UUID("123e4567-e89b-12d3-a456-426614174000"), "Test", "test@example.com")
    multi_obj = ConfigurableDrawable("union_test")
    invalid_obj = NonSerializableObject("invalid")

    # These should work
    result1 = process_drawable_or_serializable(circle)     # Should be OK - DrawableProtocol
    result2 = process_drawable_or_serializable(user)       # Should be OK - SerializableProtocol
    result3 = process_drawable_or_serializable(multi_obj)  # Should be OK - DrawableProtocol

    # This should fail type checking
    result4 = process_drawable_or_serializable(invalid_obj)  # Should cause error: implements neither protocol

    print(f"Results: {result1}, {result2}, {result3}, {result4}")


if __name__ == "__main__":
    test_runtime_checkable()
    test_dynamic_protocol_checking()
    test_protocol_combinations()
    test_union_protocols()
