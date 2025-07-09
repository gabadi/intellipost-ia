"""
Test cases for missing method detection in protocols.

This module tests whether type checkers correctly identify when classes
are missing required protocol methods.
"""

from typing import Protocol, Any, Optional
from abc import abstractmethod


class DatabaseProtocol(Protocol):
    """Protocol for database-like objects."""

    def connect(self) -> None:
        """Connect to database."""
        ...

    def disconnect(self) -> None:
        """Disconnect from database."""
        ...

    def execute(self, query: str) -> list[dict[str, Any]]:
        """Execute a query."""
        ...

    def begin_transaction(self) -> None:
        """Begin a transaction."""
        ...

    def commit(self) -> None:
        """Commit current transaction."""
        ...

    def rollback(self) -> None:
        """Rollback current transaction."""
        ...


class CacheProtocol(Protocol):
    """Protocol for cache-like objects."""

    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        ...

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value by key."""
        ...

    def delete(self, key: str) -> bool:
        """Delete value by key."""
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...


class CompleteDatabase:
    """Database implementation that implements all required methods."""

    def __init__(self):
        self.connected = False
        self.in_transaction = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def execute(self, query: str) -> list[dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Not connected")
        return [{"result": f"Query: {query}"}]

    def begin_transaction(self) -> None:
        self.in_transaction = True

    def commit(self) -> None:
        self.in_transaction = False

    def rollback(self) -> None:
        self.in_transaction = False


class IncompleteDatabase:
    """Database implementation missing required methods."""

    def __init__(self):
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def execute(self, query: str) -> list[dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Not connected")
        return [{"result": f"Query: {query}"}]

    # Missing: begin_transaction, commit, rollback


class ReadOnlyDatabase:
    """Database implementation with subset of methods."""

    def __init__(self):
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def execute(self, query: str) -> list[dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Not connected")
        return [{"result": f"Query: {query}"}]

    # Missing: begin_transaction, commit, rollback - intentionally read-only


class PartialCache:
    """Cache implementation missing some methods."""

    def __init__(self):
        self.data: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self.data.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self.data[key] = value

    # Missing: delete, clear


class CompleteCache:
    """Cache implementation with all required methods."""

    def __init__(self):
        self.data: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self.data.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self.data[key] = value

    def delete(self, key: str) -> bool:
        return self.data.pop(key, None) is not None

    def clear(self) -> None:
        self.data.clear()


class EmptyImplementation:
    """Class with no methods - should fail all protocol checks."""

    def __init__(self):
        pass


# Test functions
def use_database(db: DatabaseProtocol) -> str:
    """Use database following protocol."""
    db.connect()
    try:
        db.begin_transaction()
        results = db.execute("SELECT * FROM users")
        db.commit()
        return f"Success: {len(results)} results"
    except Exception as e:
        db.rollback()
        return f"Error: {e}"
    finally:
        db.disconnect()


def use_cache(cache: CacheProtocol) -> str:
    """Use cache following protocol."""
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    success = cache.delete("test_key")
    cache.clear()
    return f"Cache operations: value={value}, deleted={success}"


def use_both(db: DatabaseProtocol, cache: CacheProtocol) -> str:
    """Use both database and cache."""
    db_result = use_database(db)
    cache_result = use_cache(cache)
    return f"DB: {db_result}, Cache: {cache_result}"


def test_missing_methods():
    """Test missing method detection."""

    # These should work
    complete_db = CompleteDatabase()
    complete_cache = CompleteCache()

    result1 = use_database(complete_db)  # Should be OK
    result2 = use_cache(complete_cache)  # Should be OK
    result3 = use_both(complete_db, complete_cache)  # Should be OK

    # These should fail due to missing methods
    incomplete_db = IncompleteDatabase()
    readonly_db = ReadOnlyDatabase()
    partial_cache = PartialCache()
    empty_impl = EmptyImplementation()

    result4 = use_database(incomplete_db)  # Should cause error: missing transaction methods
    result5 = use_database(readonly_db)    # Should cause error: missing transaction methods
    result6 = use_cache(partial_cache)     # Should cause error: missing delete, clear
    result7 = use_database(empty_impl)     # Should cause error: missing all methods
    result8 = use_cache(empty_impl)        # Should cause error: missing all methods

    return result1, result2, result3, result4, result5, result6, result7, result8


# Test protocol with optional methods (using Union types)
from typing import Union


class OptionalMethodProtocol(Protocol):
    """Protocol with required and optional-like methods."""

    def required_method(self) -> str:
        """This method is required."""
        ...

    def optional_method(self) -> Union[str, None]:
        """This method returns None if not implemented."""
        ...


class MinimalImplementation:
    """Implementation with only required method."""

    def required_method(self) -> str:
        return "required"

    def optional_method(self) -> Union[str, None]:
        return None  # "Not implemented"


class FullImplementation:
    """Implementation with both required and optional methods."""

    def required_method(self) -> str:
        return "required"

    def optional_method(self) -> Union[str, None]:
        return "optional"


class BrokenImplementation:
    """Implementation missing required method."""

    def optional_method(self) -> Union[str, None]:
        return "optional"

    # Missing: required_method


def use_optional_protocol(obj: OptionalMethodProtocol) -> str:
    """Use protocol with optional methods."""
    required = obj.required_method()
    optional = obj.optional_method()
    return f"Required: {required}, Optional: {optional}"


def test_optional_methods():
    """Test optional method handling."""

    minimal = MinimalImplementation()
    full = FullImplementation()
    broken = BrokenImplementation()

    result1 = use_optional_protocol(minimal)  # Should be OK
    result2 = use_optional_protocol(full)     # Should be OK
    result3 = use_optional_protocol(broken)   # Should cause error: missing required_method

    return result1, result2, result3


if __name__ == "__main__":
    test_missing_methods()
    test_optional_methods()
