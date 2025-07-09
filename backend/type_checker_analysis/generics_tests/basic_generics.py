"""
Test cases for basic generic type checking.

This module tests whether type checkers correctly handle basic generic
classes, functions, and type variables.
"""

from typing import TypeVar, Generic, Any, Optional, Union, List, Dict, Callable
from uuid import UUID
from datetime import datetime


# Basic type variables
T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


class Container(Generic[T]):
    """Basic generic container class."""

    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

    def set(self, value: T) -> None:
        self.value = value

    def map(self, func: Callable[[T], U]) -> 'Container[U]':
        """Map function over container value."""
        return Container(func(self.value))


class Pair(Generic[T, U]):
    """Generic pair class with two type parameters."""

    def __init__(self, first: T, second: U):
        self.first = first
        self.second = second

    def get_first(self) -> T:
        return self.first

    def get_second(self) -> U:
        return self.second

    def swap(self) -> 'Pair[U, T]':
        """Swap the pair elements."""
        return Pair(self.second, self.first)


class Stack(Generic[T]):
    """Generic stack implementation."""

    def __init__(self):
        self._items: List[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> Optional[T]:
        if self._items:
            return self._items.pop()
        return None

    def peek(self) -> Optional[T]:
        if self._items:
            return self._items[-1]
        return None

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)


class Cache(Generic[T, U]):
    """Generic cache with key-value pairs."""

    def __init__(self):
        self._data: Dict[T, U] = {}

    def get(self, key: T) -> Optional[U]:
        return self._data.get(key)

    def set(self, key: T, value: U) -> None:
        self._data[key] = value

    def delete(self, key: T) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False

    def clear(self) -> None:
        self._data.clear()

    def keys(self) -> List[T]:
        return list(self._data.keys())

    def values(self) -> List[U]:
        return list(self._data.values())


# Generic functions
def identity(x: T) -> T:
    """Identity function."""
    return x


def first(items: List[T]) -> Optional[T]:
    """Get first item from list."""
    if items:
        return items[0]
    return None


def last(items: List[T]) -> Optional[T]:
    """Get last item from list."""
    if items:
        return items[-1]
    return None


def map_list(items: List[T], func: Callable[[T], U]) -> List[U]:
    """Map function over list items."""
    return [func(item) for item in items]


def filter_list(items: List[T], predicate: Callable[[T], bool]) -> List[T]:
    """Filter list items by predicate."""
    return [item for item in items if predicate(item)]


def reduce_list(items: List[T], func: Callable[[U, T], U], initial: U) -> U:
    """Reduce list items using function."""
    result = initial
    for item in items:
        result = func(result, item)
    return result


def combine(first: T, second: U) -> Pair[T, U]:
    """Combine two values into a pair."""
    return Pair(first, second)


# Test functions
def test_basic_generics():
    """Test basic generic functionality."""

    # Test Container[int]
    int_container = Container(42)
    int_value = int_container.get()  # Should be int
    int_container.set(100)  # Should be OK
    int_container.set("string")  # Should cause error: wrong type

    # Test Container[str]
    str_container = Container("hello")
    str_value = str_container.get()  # Should be str
    str_container.set("world")  # Should be OK
    str_container.set(123)  # Should cause error: wrong type

    # Test Pair[str, int]
    pair = Pair("key", 42)
    key = pair.get_first()  # Should be str
    value = pair.get_second()  # Should be int
    swapped = pair.swap()  # Should be Pair[int, str]

    # Test Stack[str]
    stack = Stack[str]()
    stack.push("first")  # Should be OK
    stack.push("second")  # Should be OK
    stack.push(123)  # Should cause error: wrong type

    popped = stack.pop()  # Should be Optional[str]
    peeked = stack.peek()  # Should be Optional[str]

    # Test Cache[str, int]
    cache = Cache[str, int]()
    cache.set("key1", 100)  # Should be OK
    cache.set("key2", 200)  # Should be OK
    cache.set(123, 300)  # Should cause error: wrong key type
    cache.set("key3", "value")  # Should cause error: wrong value type

    cached_value = cache.get("key1")  # Should be Optional[int]
    keys = cache.keys()  # Should be List[str]
    values = cache.values()  # Should be List[int]

    return int_value, str_value, key, value, swapped, popped, peeked, cached_value, keys, values


def test_generic_functions():
    """Test generic functions."""

    # Test identity function
    int_id = identity(42)  # Should be int
    str_id = identity("hello")  # Should be str

    # Test first function
    int_list = [1, 2, 3, 4, 5]
    str_list = ["a", "b", "c"]

    first_int = first(int_list)  # Should be Optional[int]
    first_str = first(str_list)  # Should be Optional[str]
    first_empty = first([])  # Should be Optional[T] where T is inferred

    # Test last function
    last_int = last(int_list)  # Should be Optional[int]
    last_str = last(str_list)  # Should be Optional[str]

    # Test map_list function
    doubled = map_list(int_list, lambda x: x * 2)  # Should be List[int]
    lengths = map_list(str_list, lambda x: len(x))  # Should be List[int]
    uppercased = map_list(str_list, lambda x: x.upper())  # Should be List[str]

    # Test filter_list function
    evens = filter_list(int_list, lambda x: x % 2 == 0)  # Should be List[int]
    long_strings = filter_list(str_list, lambda x: len(x) > 1)  # Should be List[str]

    # Test reduce_list function
    sum_ints = reduce_list(int_list, lambda acc, x: acc + x, 0)  # Should be int
    concat_strings = reduce_list(str_list, lambda acc, x: acc + x, "")  # Should be str

    # Test combine function
    int_str_pair = combine(42, "hello")  # Should be Pair[int, str]
    str_int_pair = combine("world", 100)  # Should be Pair[str, int]

    return (int_id, str_id, first_int, first_str, last_int, last_str,
            doubled, lengths, uppercased, evens, long_strings,
            sum_ints, concat_strings, int_str_pair, str_int_pair)


def test_generic_type_errors():
    """Test generic type errors."""

    # These should cause type errors
    int_container = Container(42)

    # Wrong type assignment
    int_container.set("string")  # Error: expected int, got str

    # Wrong type in stack
    int_stack = Stack[int]()
    int_stack.push("string")  # Error: expected int, got str

    # Wrong type in cache
    str_int_cache = Cache[str, int]()
    str_int_cache.set(123, 456)  # Error: expected str key, got int
    str_int_cache.set("key", "value")  # Error: expected int value, got str

    # Wrong type in pair
    str_int_pair = Pair("hello", 42)
    int_str_pair = Pair(42, "hello")

    # Type mismatch in assignment
    wrong_assignment: Pair[int, str] = str_int_pair  # Error: types don't match

    # Wrong function parameter types
    int_list = [1, 2, 3]
    str_list = ["a", "b", "c"]

    # Function expecting int list but getting str list
    def process_ints(items: List[int]) -> int:
        return sum(items)

    result1 = process_ints(int_list)  # Should be OK
    result2 = process_ints(str_list)  # Error: expected List[int], got List[str]

    # Function expecting specific generic type
    def process_int_container(container: Container[int]) -> int:
        return container.get()

    int_container = Container(42)
    str_container = Container("hello")

    result3 = process_int_container(int_container)  # Should be OK
    result4 = process_int_container(str_container)  # Error: expected Container[int], got Container[str]

    return result1, result2, result3, result4


def test_generic_inheritance():
    """Test generic inheritance scenarios."""

    class SpecializedContainer(Container[str]):
        """Container specialized for strings."""

        def upper(self) -> str:
            return self.value.upper()

        def lower(self) -> str:
            return self.value.lower()

    class ExtendedContainer(Container[T]):
        """Extended container with additional methods."""

        def is_none(self) -> bool:
            return self.value is None

        def transform(self, func: Callable[[T], T]) -> T:
            self.value = func(self.value)
            return self.value

    # Test specialized container
    specialized = SpecializedContainer("Hello")
    upper_val = specialized.upper()  # Should be str
    lower_val = specialized.lower()  # Should be str
    str_val = specialized.get()  # Should be str

    specialized.set("World")  # Should be OK
    specialized.set(123)  # Should cause error: expected str, got int

    # Test extended container
    int_extended = ExtendedContainer(42)
    str_extended = ExtendedContainer("test")

    int_none_check = int_extended.is_none()  # Should be bool
    str_none_check = str_extended.is_none()  # Should be bool

    int_transformed = int_extended.transform(lambda x: x * 2)  # Should be int
    str_transformed = str_extended.transform(lambda x: x.upper())  # Should be str

    # Type errors in extended container
    int_extended.set("string")  # Error: expected int, got str
    str_extended.set(123)  # Error: expected str, got int

    return (upper_val, lower_val, str_val, int_none_check, str_none_check,
            int_transformed, str_transformed)


def test_generic_with_constraints():
    """Test generics with basic constraints using built-in types."""

    # This function should work with any type that supports len()
    def get_length(item: T) -> int:
        return len(item)  # This will fail at runtime for types without len()

    # These should work
    str_len = get_length("hello")  # Should be int
    list_len = get_length([1, 2, 3])  # Should be int
    dict_len = get_length({"a": 1, "b": 2})  # Should be int

    # This should cause a runtime error but type checkers might not catch it
    int_len = get_length(42)  # Runtime error: int has no len()

    return str_len, list_len, dict_len, int_len


if __name__ == "__main__":
    test_basic_generics()
    test_generic_functions()
    test_generic_type_errors()
    test_generic_inheritance()
    test_generic_with_constraints()
