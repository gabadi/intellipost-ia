"""
Test cases for generic type constraints and bounds.

This module tests whether type checkers correctly handle TypeVar constraints,
bounds, and more advanced generic typing scenarios.
"""

from typing import TypeVar, Generic, Protocol, Any, Optional, Union, List, Dict, Callable
from abc import ABC, abstractmethod
from numbers import Number
from collections.abc import Iterable, Sized


# Type variables with constraints
Numeric = TypeVar('Numeric', int, float, complex)
StringOrBytes = TypeVar('StringOrBytes', str, bytes)
Comparable = TypeVar('Comparable', bound='SupportsComparison')


# Type variable with bound
class SupportsComparison(Protocol):
    """Protocol for objects that support comparison."""

    def __lt__(self, other: Any) -> bool:
        ...

    def __le__(self, other: Any) -> bool:
        ...

    def __gt__(self, other: Any) -> bool:
        ...

    def __ge__(self, other: Any) -> bool:
        ...


# Type variable with protocol bound
Serializable = TypeVar('Serializable', bound='SupportsSerialize')


class SupportsSerialize(Protocol):
    """Protocol for objects that can be serialized."""

    def serialize(self) -> dict[str, Any]:
        ...


# Type variable with ABC bound
Drawable = TypeVar('Drawable', bound='DrawableABC')


class DrawableABC(ABC):
    """Abstract base class for drawable objects."""

    @abstractmethod
    def draw(self) -> None:
        ...

    @abstractmethod
    def get_bounds(self) -> tuple[int, int, int, int]:
        ...


# Classes for testing
class Point:
    """Point class that supports comparison."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __lt__(self, other: 'Point') -> bool:
        return (self.x**2 + self.y**2) < (other.x**2 + other.y**2)

    def __le__(self, other: 'Point') -> bool:
        return (self.x**2 + self.y**2) <= (other.x**2 + other.y**2)

    def __gt__(self, other: 'Point') -> bool:
        return (self.x**2 + self.y**2) > (other.x**2 + other.y**2)

    def __ge__(self, other: 'Point') -> bool:
        return (self.x**2 + self.y**2) >= (other.x**2 + other.y**2)


class User:
    """User class that supports serialization."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def serialize(self) -> dict[str, Any]:
        return {"name": self.name, "age": self.age}


class Circle(DrawableABC):
    """Circle class that implements DrawableABC."""

    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self) -> None:
        print(f"Drawing circle at ({self.x}, {self.y}) with radius {self.radius}")

    def get_bounds(self) -> tuple[int, int, int, int]:
        return (int(self.x - self.radius), int(self.y - self.radius),
                int(2 * self.radius), int(2 * self.radius))


class Rectangle(DrawableABC):
    """Rectangle class that implements DrawableABC."""

    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self) -> None:
        print(f"Drawing rectangle at ({self.x}, {self.y}) with size {self.width}x{self.height}")

    def get_bounds(self) -> tuple[int, int, int, int]:
        return (int(self.x), int(self.y), int(self.width), int(self.height))


class NonComparable:
    """Class that doesn't support comparison."""

    def __init__(self, value: str):
        self.value = value


class NonSerializable:
    """Class that doesn't support serialization."""

    def __init__(self, value: str):
        self.value = value


class NonDrawable:
    """Class that doesn't inherit from DrawableABC."""

    def __init__(self, name: str):
        self.name = name


# Functions using constrained type variables
def add_numbers(a: Numeric, b: Numeric) -> Numeric:
    """Add two numbers - should work with int, float, or complex."""
    return a + b


def multiply_numbers(a: Numeric, b: Numeric) -> Numeric:
    """Multiply two numbers - should work with int, float, or complex."""
    return a * b


def process_string_or_bytes(data: StringOrBytes) -> int:
    """Process string or bytes data - should work with str or bytes."""
    return len(data)


def encode_string_or_bytes(data: StringOrBytes) -> bytes:
    """Encode string or bytes data."""
    if isinstance(data, str):
        return data.encode('utf-8')
    return data


def find_max(items: List[Comparable]) -> Optional[Comparable]:
    """Find maximum item in list - requires comparable items."""
    if not items:
        return None

    max_item = items[0]
    for item in items[1:]:
        if item > max_item:
            max_item = item
    return max_item


def find_min(items: List[Comparable]) -> Optional[Comparable]:
    """Find minimum item in list - requires comparable items."""
    if not items:
        return None

    min_item = items[0]
    for item in items[1:]:
        if item < min_item:
            min_item = item
    return min_item


def sort_items(items: List[Comparable]) -> List[Comparable]:
    """Sort items - requires comparable items."""
    return sorted(items)


def serialize_object(obj: Serializable) -> dict[str, Any]:
    """Serialize object - requires serializable object."""
    return obj.serialize()


def draw_object(obj: Drawable) -> None:
    """Draw object - requires drawable object."""
    obj.draw()


def get_object_bounds(obj: Drawable) -> tuple[int, int, int, int]:
    """Get object bounds - requires drawable object."""
    return obj.get_bounds()


# Generic classes with constraints
class NumberContainer(Generic[Numeric]):
    """Container for numeric types only."""

    def __init__(self, value: Numeric):
        self.value = value

    def add(self, other: Numeric) -> Numeric:
        return self.value + other

    def multiply(self, other: Numeric) -> Numeric:
        return self.value * other


class ComparableContainer(Generic[Comparable]):
    """Container for comparable types."""

    def __init__(self, value: Comparable):
        self.value = value

    def is_greater_than(self, other: Comparable) -> bool:
        return self.value > other

    def is_less_than(self, other: Comparable) -> bool:
        return self.value < other


class SerializableContainer(Generic[Serializable]):
    """Container for serializable types."""

    def __init__(self, value: Serializable):
        self.value = value

    def serialize(self) -> dict[str, Any]:
        return self.value.serialize()


class DrawableContainer(Generic[Drawable]):
    """Container for drawable types."""

    def __init__(self, value: Drawable):
        self.value = value

    def draw(self) -> None:
        self.value.draw()

    def get_bounds(self) -> tuple[int, int, int, int]:
        return self.value.get_bounds()


# Test functions
def test_numeric_constraints():
    """Test numeric type constraints."""

    # These should work
    int_result = add_numbers(5, 10)  # Should be int
    float_result = add_numbers(3.14, 2.86)  # Should be float
    complex_result = add_numbers(1+2j, 3+4j)  # Should be complex

    int_mult = multiply_numbers(2, 3)  # Should be int
    float_mult = multiply_numbers(2.5, 4.0)  # Should be float
    complex_mult = multiply_numbers(1+1j, 2+2j)  # Should be complex

    # These should cause type errors
    string_result = add_numbers("hello", "world")  # Error: str not in constraints
    bool_result = add_numbers(True, False)  # Error: bool not in constraints

    # Test NumberContainer
    int_container = NumberContainer(42)
    float_container = NumberContainer(3.14)
    complex_container = NumberContainer(1+2j)

    int_added = int_container.add(10)  # Should be int
    float_added = float_container.add(2.86)  # Should be float
    complex_added = complex_container.add(3+4j)  # Should be complex

    # These should cause type errors
    string_container = NumberContainer("hello")  # Error: str not in constraints

    return (int_result, float_result, complex_result, int_mult, float_mult,
            complex_mult, string_result, bool_result, int_added, float_added,
            complex_added)


def test_string_or_bytes_constraints():
    """Test string or bytes constraints."""

    # These should work
    str_length = process_string_or_bytes("hello")  # Should be int
    bytes_length = process_string_or_bytes(b"hello")  # Should be int

    str_encoded = encode_string_or_bytes("hello")  # Should be bytes
    bytes_encoded = encode_string_or_bytes(b"hello")  # Should be bytes

    # These should cause type errors
    int_length = process_string_or_bytes(42)  # Error: int not in constraints
    list_length = process_string_or_bytes([1, 2, 3])  # Error: list not in constraints

    return str_length, bytes_length, str_encoded, bytes_encoded, int_length, list_length


def test_comparable_constraints():
    """Test comparable type constraints."""

    # These should work
    int_list = [1, 5, 3, 9, 2]
    float_list = [1.1, 5.5, 3.3, 9.9, 2.2]
    str_list = ["apple", "banana", "cherry"]
    point_list = [Point(1, 2), Point(3, 4), Point(0, 1)]

    max_int = find_max(int_list)  # Should be Optional[int]
    max_float = find_max(float_list)  # Should be Optional[float]
    max_str = find_max(str_list)  # Should be Optional[str]
    max_point = find_max(point_list)  # Should be Optional[Point]

    min_int = find_min(int_list)  # Should be Optional[int]
    min_float = find_min(float_list)  # Should be Optional[float]
    min_str = find_min(str_list)  # Should be Optional[str]
    min_point = find_min(point_list)  # Should be Optional[Point]

    sorted_int = sort_items(int_list)  # Should be List[int]
    sorted_float = sort_items(float_list)  # Should be List[float]
    sorted_str = sort_items(str_list)  # Should be List[str]
    sorted_point = sort_items(point_list)  # Should be List[Point]

    # These should cause type errors
    non_comparable_list = [NonComparable("a"), NonComparable("b")]
    max_non_comparable = find_max(non_comparable_list)  # Error: doesn't support comparison

    # Test ComparableContainer
    int_comp_container = ComparableContainer(42)
    str_comp_container = ComparableContainer("hello")
    point_comp_container = ComparableContainer(Point(1, 2))

    int_greater = int_comp_container.is_greater_than(30)  # Should be bool
    str_greater = str_comp_container.is_greater_than("goodbye")  # Should be bool
    point_greater = point_comp_container.is_greater_than(Point(0, 0))  # Should be bool

    # These should cause type errors
    non_comp_container = ComparableContainer(NonComparable("test"))  # Error: doesn't support comparison

    return (max_int, max_float, max_str, max_point, min_int, min_float, min_str, min_point,
            sorted_int, sorted_float, sorted_str, sorted_point, max_non_comparable,
            int_greater, str_greater, point_greater)


def test_serializable_constraints():
    """Test serializable type constraints."""

    user = User("Alice", 30)

    # These should work
    user_data = serialize_object(user)  # Should be dict[str, Any]

    # Test SerializableContainer
    user_container = SerializableContainer(user)
    serialized = user_container.serialize()  # Should be dict[str, Any]

    # These should cause type errors
    non_serializable = NonSerializable("test")
    non_serializable_data = serialize_object(non_serializable)  # Error: doesn't support serialization

    non_serializable_container = SerializableContainer(non_serializable)  # Error: doesn't support serialization

    return user_data, serialized, non_serializable_data


def test_drawable_constraints():
    """Test drawable type constraints."""

    circle = Circle(10, 20, 5)
    rectangle = Rectangle(0, 0, 100, 50)

    # These should work
    draw_object(circle)  # Should be OK
    draw_object(rectangle)  # Should be OK

    circle_bounds = get_object_bounds(circle)  # Should be tuple[int, int, int, int]
    rectangle_bounds = get_object_bounds(rectangle)  # Should be tuple[int, int, int, int]

    # Test DrawableContainer
    circle_container = DrawableContainer(circle)
    rectangle_container = DrawableContainer(rectangle)

    circle_container.draw()  # Should be OK
    rectangle_container.draw()  # Should be OK

    circle_container_bounds = circle_container.get_bounds()  # Should be tuple[int, int, int, int]
    rectangle_container_bounds = rectangle_container.get_bounds()  # Should be tuple[int, int, int, int]

    # These should cause type errors
    non_drawable = NonDrawable("test")
    draw_object(non_drawable)  # Error: doesn't inherit from DrawableABC

    non_drawable_container = DrawableContainer(non_drawable)  # Error: doesn't inherit from DrawableABC

    return (circle_bounds, rectangle_bounds, circle_container_bounds,
            rectangle_container_bounds)


def test_multiple_constraints():
    """Test functions with multiple type constraints."""

    # Type variable with multiple constraints
    MultiType = TypeVar('MultiType', int, str, Point)

    def process_multi(value: MultiType) -> str:
        """Process value that can be int, str, or Point."""
        if isinstance(value, int):
            return f"Integer: {value}"
        elif isinstance(value, str):
            return f"String: {value}"
        elif isinstance(value, Point):
            return f"Point: ({value.x}, {value.y})"
        else:
            return "Unknown type"

    # These should work
    int_result = process_multi(42)  # Should be str
    str_result = process_multi("hello")  # Should be str
    point_result = process_multi(Point(1, 2))  # Should be str

    # These should cause type errors
    float_result = process_multi(3.14)  # Error: float not in constraints
    user_result = process_multi(User("Alice", 30))  # Error: User not in constraints

    return int_result, str_result, point_result, float_result, user_result


def test_bound_vs_constraint():
    """Test difference between bound and constraint."""

    # Bound allows subclasses
    BoundedType = TypeVar('BoundedType', bound=DrawableABC)

    def draw_bounded(obj: BoundedType) -> BoundedType:
        """Draw object that inherits from DrawableABC."""
        obj.draw()
        return obj

    # Constraint only allows specific types
    ConstrainedType = TypeVar('ConstrainedType', Circle, Rectangle)

    def draw_constrained(obj: ConstrainedType) -> ConstrainedType:
        """Draw object that is exactly Circle or Rectangle."""
        obj.draw()
        return obj

    circle = Circle(0, 0, 5)
    rectangle = Rectangle(0, 0, 10, 20)

    # Both should work with bound
    circle_bounded = draw_bounded(circle)  # Should be Circle
    rectangle_bounded = draw_bounded(rectangle)  # Should be Rectangle

    # Both should work with constraint
    circle_constrained = draw_constrained(circle)  # Should be Circle
    rectangle_constrained = draw_constrained(rectangle)  # Should be Rectangle

    # Test with subclass
    class ColoredCircle(Circle):
        def __init__(self, x: float, y: float, radius: float, color: str):
            super().__init__(x, y, radius)
            self.color = color

    colored_circle = ColoredCircle(0, 0, 5, "red")

    # Should work with bound (allows subclasses)
    colored_bounded = draw_bounded(colored_circle)  # Should be ColoredCircle

    # Should fail with constraint (only allows exact types)
    colored_constrained = draw_constrained(colored_circle)  # Error: ColoredCircle not in constraints

    return (circle_bounded, rectangle_bounded, circle_constrained, rectangle_constrained,
            colored_bounded, colored_constrained)


if __name__ == "__main__":
    test_numeric_constraints()
    test_string_or_bytes_constraints()
    test_comparable_constraints()
    test_serializable_constraints()
    test_drawable_constraints()
    test_multiple_constraints()
    test_bound_vs_constraint()
