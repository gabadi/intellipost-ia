"""
Test cases for combining generics with protocols.

This module tests whether type checkers correctly handle generic protocols
and their interaction with type variables and constraints.
"""

from typing import TypeVar, Generic, Protocol, Any, Optional, List, Dict, Callable, Union
from typing_extensions import runtime_checkable
from abc import ABC, abstractmethod


# Type variables
T = TypeVar('T')
U = TypeVar('U')
K = TypeVar('K')
V = TypeVar('V')


# Generic protocols
class Container(Protocol[T]):
    """Protocol for container-like objects."""

    def get(self) -> T:
        """Get the contained value."""
        ...

    def set(self, value: T) -> None:
        """Set the contained value."""
        ...


class Repository(Protocol[T]):
    """Protocol for repository-like objects."""

    def save(self, item: T) -> T:
        """Save an item."""
        ...

    def find_by_id(self, item_id: str) -> Optional[T]:
        """Find item by ID."""
        ...

    def find_all(self) -> List[T]:
        """Find all items."""
        ...

    def delete(self, item_id: str) -> bool:
        """Delete item by ID."""
        ...


class Mapper(Protocol[T, U]):
    """Protocol for mapping objects from one type to another."""

    def map(self, source: T) -> U:
        """Map source to target type."""
        ...

    def reverse_map(self, target: U) -> T:
        """Map target back to source type."""
        ...


class Cache(Protocol[K, V]):
    """Protocol for cache-like objects."""

    def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        ...

    def set(self, key: K, value: V) -> None:
        """Set value by key."""
        ...

    def delete(self, key: K) -> bool:
        """Delete value by key."""
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...


@runtime_checkable
class Serializable(Protocol[T]):
    """Protocol for objects that can be serialized."""

    def serialize(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        ...

    def deserialize(self, data: Dict[str, Any]) -> T:
        """Deserialize from dictionary."""
        ...


class Validator(Protocol[T]):
    """Protocol for validation objects."""

    def validate(self, item: T) -> bool:
        """Validate an item."""
        ...

    def get_errors(self, item: T) -> List[str]:
        """Get validation errors."""
        ...


class Comparable(Protocol[T]):
    """Protocol for comparable objects."""

    def compare(self, other: T) -> int:
        """Compare with another object. Returns -1, 0, or 1."""
        ...

    def equals(self, other: T) -> bool:
        """Check equality with another object."""
        ...


# Test classes
class User:
    """User class for testing."""

    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def __str__(self) -> str:
        return f"User(id={self.user_id}, name={self.name}, email={self.email})"


class Product:
    """Product class for testing."""

    def __init__(self, product_id: str, name: str, price: float):
        self.product_id = product_id
        self.name = name
        self.price = price

    def __str__(self) -> str:
        return f"Product(id={self.product_id}, name={self.name}, price={self.price})"


# Implementations
class SimpleContainer(Generic[T]):
    """Simple container implementation."""

    def __init__(self, value: T):
        self._value = value

    def get(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        self._value = value


class InMemoryRepository(Generic[T]):
    """In-memory repository implementation."""

    def __init__(self):
        self._items: Dict[str, T] = {}

    def save(self, item: T) -> T:
        # Assume item has an 'id' attribute
        item_id = getattr(item, 'user_id', None) or getattr(item, 'product_id', None)
        if item_id:
            self._items[item_id] = item
        return item

    def find_by_id(self, item_id: str) -> Optional[T]:
        return self._items.get(item_id)

    def find_all(self) -> List[T]:
        return list(self._items.values())

    def delete(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False


class UserToProductMapper:
    """Mapper from User to Product."""

    def map(self, user: User) -> Product:
        return Product(f"prod_{user.user_id}", f"Product for {user.name}", 99.99)

    def reverse_map(self, product: Product) -> User:
        user_id = product.product_id.replace("prod_", "")
        return User(user_id, f"User for {product.name}", f"user_{user_id}@example.com")


class StringIntMapper:
    """Mapper from string to int."""

    def map(self, source: str) -> int:
        return hash(source)

    def reverse_map(self, target: int) -> str:
        return str(target)


class DictCache(Generic[K, V]):
    """Dictionary-based cache implementation."""

    def __init__(self):
        self._data: Dict[K, V] = {}

    def get(self, key: K) -> Optional[V]:
        return self._data.get(key)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def delete(self, key: K) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False

    def clear(self) -> None:
        self._data.clear()


class UserSerializer:
    """Serializer for User objects."""

    def serialize(self, user: User) -> Dict[str, Any]:
        return {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email
        }

    def deserialize(self, data: Dict[str, Any]) -> User:
        return User(data["user_id"], data["name"], data["email"])


class ProductSerializer:
    """Serializer for Product objects."""

    def serialize(self, product: Product) -> Dict[str, Any]:
        return {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price
        }

    def deserialize(self, data: Dict[str, Any]) -> Product:
        return Product(data["product_id"], data["name"], data["price"])


class UserValidator:
    """Validator for User objects."""

    def validate(self, user: User) -> bool:
        errors = self.get_errors(user)
        return len(errors) == 0

    def get_errors(self, user: User) -> List[str]:
        errors = []
        if not user.user_id:
            errors.append("User ID is required")
        if not user.name:
            errors.append("Name is required")
        if not user.email or "@" not in user.email:
            errors.append("Valid email is required")
        return errors


class ProductValidator:
    """Validator for Product objects."""

    def validate(self, product: Product) -> bool:
        errors = self.get_errors(product)
        return len(errors) == 0

    def get_errors(self, product: Product) -> List[str]:
        errors = []
        if not product.product_id:
            errors.append("Product ID is required")
        if not product.name:
            errors.append("Name is required")
        if product.price <= 0:
            errors.append("Price must be positive")
        return errors


class UserComparator:
    """Comparator for User objects."""

    def compare(self, user1: User, user2: User) -> int:
        if user1.name < user2.name:
            return -1
        elif user1.name > user2.name:
            return 1
        else:
            return 0

    def equals(self, user1: User, user2: User) -> bool:
        return user1.user_id == user2.user_id


# Test functions
def test_generic_protocols():
    """Test basic generic protocol functionality."""

    # Test Container protocol
    user_container = SimpleContainer(User("1", "Alice", "alice@example.com"))
    product_container = SimpleContainer(Product("1", "Widget", 29.99))

    def use_container(container: Container[T]) -> T:
        value = container.get()
        container.set(value)  # Set same value back
        return value

    user_result = use_container(user_container)  # Should be User
    product_result = use_container(product_container)  # Should be Product

    # Test Repository protocol
    user_repo = InMemoryRepository[User]()
    product_repo = InMemoryRepository[Product]()

    def use_repository(repo: Repository[T], item: T) -> Optional[T]:
        saved = repo.save(item)
        # Find by ID (assuming item has appropriate ID attribute)
        item_id = getattr(item, 'user_id', None) or getattr(item, 'product_id', None)
        return repo.find_by_id(item_id) if item_id else None

    user = User("1", "Bob", "bob@example.com")
    product = Product("1", "Gadget", 49.99)

    saved_user = use_repository(user_repo, user)  # Should be Optional[User]
    saved_product = use_repository(product_repo, product)  # Should be Optional[Product]

    return user_result, product_result, saved_user, saved_product


def test_multi_generic_protocols():
    """Test protocols with multiple type parameters."""

    # Test Mapper protocol
    user_to_product_mapper = UserToProductMapper()
    string_to_int_mapper = StringIntMapper()

    def use_mapper(mapper: Mapper[T, U], source: T) -> U:
        target = mapper.map(source)
        return target

    user = User("1", "Charlie", "charlie@example.com")
    product = use_mapper(user_to_product_mapper, user)  # Should be Product

    string_val = "hello"
    int_val = use_mapper(string_to_int_mapper, string_val)  # Should be int

    # Test Cache protocol
    str_int_cache = DictCache[str, int]()
    int_user_cache = DictCache[int, User]()

    def use_cache(cache: Cache[K, V], key: K, value: V) -> Optional[V]:
        cache.set(key, value)
        return cache.get(key)

    cached_int = use_cache(str_int_cache, "key1", 42)  # Should be Optional[int]
    cached_user = use_cache(int_user_cache, 1, user)  # Should be Optional[User]

    return product, int_val, cached_int, cached_user


def test_protocol_type_errors():
    """Test type errors with generic protocols."""

    user_container = SimpleContainer(User("1", "Dave", "dave@example.com"))
    product_container = SimpleContainer(Product("1", "Tool", 19.99))

    # These should cause type errors
    def use_user_container(container: Container[User]) -> User:
        return container.get()

    user_result = use_user_container(user_container)  # Should be OK
    product_result = use_user_container(product_container)  # Error: Product container is not User container

    # Wrong type assignment
    user_container.set(User("2", "Eve", "eve@example.com"))  # Should be OK
    user_container.set(Product("2", "Item", 9.99))  # Error: Product is not User

    # Wrong repository type
    user_repo = InMemoryRepository[User]()
    product_repo = InMemoryRepository[Product]()

    def use_user_repo(repo: Repository[User]) -> List[User]:
        return repo.find_all()

    users = use_user_repo(user_repo)  # Should be OK
    products = use_user_repo(product_repo)  # Error: Product repository is not User repository

    return user_result, product_result, users, products


def test_protocol_inheritance():
    """Test protocol inheritance with generics."""

    class ExtendedContainer(Container[T], Protocol):
        """Extended container protocol with additional methods."""

        def is_empty(self) -> bool:
            """Check if container is empty."""
            ...

        def clear(self) -> None:
            """Clear the container."""
            ...

    class AdvancedContainer(Generic[T]):
        """Advanced container implementation."""

        def __init__(self, value: Optional[T] = None):
            self._value = value

        def get(self) -> T:
            if self._value is None:
                raise ValueError("Container is empty")
            return self._value

        def set(self, value: T) -> None:
            self._value = value

        def is_empty(self) -> bool:
            return self._value is None

        def clear(self) -> None:
            self._value = None

    # Test extended protocol
    advanced_container = AdvancedContainer[str]()

    def use_extended_container(container: ExtendedContainer[T]) -> bool:
        if container.is_empty():
            return True
        value = container.get()
        container.clear()
        return False

    result = use_extended_container(advanced_container)  # Should be bool

    # Test with base protocol
    def use_base_container(container: Container[T]) -> T:
        return container.get()

    # Should work with extended implementation
    advanced_container.set("test")
    base_result = use_base_container(advanced_container)  # Should be str

    return result, base_result


def test_runtime_checkable_generic_protocols():
    """Test runtime_checkable with generic protocols."""

    @runtime_checkable
    class ProcessorProtocol(Protocol[T]):
        """Runtime checkable processor protocol."""

        def process(self, item: T) -> T:
            """Process an item."""
            ...

    class StringProcessor:
        """String processor implementation."""

        def process(self, item: str) -> str:
            return item.upper()

    class IntProcessor:
        """Integer processor implementation."""

        def process(self, item: int) -> int:
            return item * 2

    class NonProcessor:
        """Class that doesn't implement the protocol."""

        def do_something(self, item: str) -> str:
            return item

    # Test isinstance checks
    string_processor = StringProcessor()
    int_processor = IntProcessor()
    non_processor = NonProcessor()

    print(f"string_processor isinstance ProcessorProtocol: {isinstance(string_processor, ProcessorProtocol)}")
    print(f"int_processor isinstance ProcessorProtocol: {isinstance(int_processor, ProcessorProtocol)}")
    print(f"non_processor isinstance ProcessorProtocol: {isinstance(non_processor, ProcessorProtocol)}")

    # Test dynamic usage
    def use_processor(processor: ProcessorProtocol[T], item: T) -> T:
        return processor.process(item)

    # These should work
    str_result = use_processor(string_processor, "hello")  # Should be str
    int_result = use_processor(int_processor, 42)  # Should be int

    # This should fail at type check time
    non_result = use_processor(non_processor, "test")  # Error: doesn't implement protocol

    return str_result, int_result, non_result


def test_protocol_composition():
    """Test composition of generic protocols."""

    class PersistentContainer(Container[T], Serializable[T], Protocol):
        """Container that is also serializable."""

        def save_to_file(self, filename: str) -> None:
            """Save container to file."""
            ...

        def load_from_file(self, filename: str) -> None:
            """Load container from file."""
            ...

    class FilePersistentContainer(Generic[T]):
        """File-persistent container implementation."""

        def __init__(self, value: T, serializer: Serializable[T]):
            self._value = value
            self._serializer = serializer

        def get(self) -> T:
            return self._value

        def set(self, value: T) -> None:
            self._value = value

        def serialize(self) -> Dict[str, Any]:
            return self._serializer.serialize(self._value)

        def deserialize(self, data: Dict[str, Any]) -> T:
            self._value = self._serializer.deserialize(data)
            return self._value

        def save_to_file(self, filename: str) -> None:
            # Implementation would save to file
            pass

        def load_from_file(self, filename: str) -> None:
            # Implementation would load from file
            pass

    # Test composition
    user_serializer = UserSerializer()
    persistent_container = FilePersistentContainer(User("1", "Frank", "frank@example.com"), user_serializer)

    def use_persistent_container(container: PersistentContainer[T]) -> Dict[str, Any]:
        value = container.get()
        container.save_to_file("test.json")
        return container.serialize()

    serialized = use_persistent_container(persistent_container)  # Should be Dict[str, Any]

    return serialized


def test_constrained_generic_protocols():
    """Test generic protocols with type constraints."""

    # Type variable with constraint
    Numeric = TypeVar('Numeric', int, float, complex)

    class Calculator(Protocol[Numeric]):
        """Calculator protocol for numeric types."""

        def add(self, a: Numeric, b: Numeric) -> Numeric:
            """Add two numbers."""
            ...

        def multiply(self, a: Numeric, b: Numeric) -> Numeric:
            """Multiply two numbers."""
            ...

    class IntCalculator:
        """Integer calculator implementation."""

        def add(self, a: int, b: int) -> int:
            return a + b

        def multiply(self, a: int, b: int) -> int:
            return a * b

    class FloatCalculator:
        """Float calculator implementation."""

        def add(self, a: float, b: float) -> float:
            return a + b

        def multiply(self, a: float, b: float) -> float:
            return a * b

    class StringCalculator:
        """String "calculator" - should not work with numeric constraint."""

        def add(self, a: str, b: str) -> str:
            return a + b

        def multiply(self, a: str, b: str) -> str:
            return a * len(b)

    # Test with constrained protocol
    int_calc = IntCalculator()
    float_calc = FloatCalculator()
    string_calc = StringCalculator()

    def use_calculator(calc: Calculator[Numeric], a: Numeric, b: Numeric) -> Numeric:
        return calc.add(a, b)

    # These should work
    int_result = use_calculator(int_calc, 5, 10)  # Should be int
    float_result = use_calculator(float_calc, 3.14, 2.86)  # Should be float

    # This should fail
    string_result = use_calculator(string_calc, "hello", "world")  # Error: str not in constraints

    return int_result, float_result, string_result


if __name__ == "__main__":
    test_generic_protocols()
    test_multi_generic_protocols()
    test_protocol_type_errors()
    test_protocol_inheritance()
    test_runtime_checkable_generic_protocols()
    test_protocol_composition()
    test_constrained_generic_protocols()
