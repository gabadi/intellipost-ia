"""
Test cases for structural subtyping behavior in protocols.

This module tests whether type checkers correctly identify structural subtyping
violations and compatibility issues with protocols.
"""

from typing import Protocol, Any, Optional
from uuid import UUID


class UserProtocol(Protocol):
    """Protocol for user-like objects."""

    def get_id(self) -> UUID:
        """Get user ID."""
        ...

    def get_name(self) -> str:
        """Get user name."""
        ...

    def is_active(self) -> bool:
        """Check if user is active."""
        ...


class ExtendedUserProtocol(Protocol):
    """Extended protocol with additional methods."""

    def get_id(self) -> UUID:
        """Get user ID."""
        ...

    def get_name(self) -> str:
        """Get user name."""
        ...

    def is_active(self) -> bool:
        """Check if user is active."""
        ...

    def get_email(self) -> str:
        """Get user email."""
        ...

    def get_roles(self) -> list[str]:
        """Get user roles."""
        ...


class CompliantUser:
    """Class that correctly implements UserProtocol."""

    def __init__(self, user_id: UUID, name: str, active: bool = True):
        self.user_id = user_id
        self.name = name
        self.active = active

    def get_id(self) -> UUID:
        return self.user_id

    def get_name(self) -> str:
        return self.name

    def is_active(self) -> bool:
        return self.active


class NonCompliantUser:
    """Class that does NOT implement UserProtocol correctly."""

    def __init__(self, user_id: UUID, name: str):
        self.user_id = user_id
        self.name = name

    def get_id(self) -> UUID:
        return self.user_id

    def get_name(self) -> str:
        return self.name

    # Missing is_active method - should cause protocol violation


class WrongSignatureUser:
    """Class with wrong method signatures."""

    def __init__(self, user_id: UUID, name: str):
        self.user_id = user_id
        self.name = name

    def get_id(self) -> str:  # Wrong return type - should be UUID
        return str(self.user_id)

    def get_name(self) -> str:
        return self.name

    def is_active(self, check_db: bool = False) -> bool:  # Wrong signature - should not have parameters
        return True


class PartiallyCompliantUser:
    """Class that implements more than required."""

    def __init__(self, user_id: UUID, name: str, email: str, active: bool = True):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.active = active

    def get_id(self) -> UUID:
        return self.user_id

    def get_name(self) -> str:
        return self.name

    def is_active(self) -> bool:
        return self.active

    def get_email(self) -> str:  # Extra method - should still be protocol compliant
        return self.email


# Test functions that should detect protocol violations
def process_user(user: UserProtocol) -> str:
    """Process a user that conforms to UserProtocol."""
    return f"User {user.get_name()} (ID: {user.get_id()}) is {'active' if user.is_active() else 'inactive'}"


def process_extended_user(user: ExtendedUserProtocol) -> str:
    """Process a user that conforms to ExtendedUserProtocol."""
    return f"User {user.get_name()} ({user.get_email()}) has roles: {', '.join(user.get_roles())}"


# Test cases - these should generate type errors
def test_protocol_violations():
    """Test protocol violations - these should be caught by type checkers."""

    # This should work - compliant implementation
    compliant = CompliantUser(UUID("123e4567-e89b-12d3-a456-426614174000"), "John Doe")
    result1 = process_user(compliant)  # Should be OK

    # This should fail - missing method
    non_compliant = NonCompliantUser(UUID("123e4567-e89b-12d3-a456-426614174000"), "Jane Smith")
    result2 = process_user(non_compliant)  # Should cause error: missing is_active method

    # This should fail - wrong signature
    wrong_sig = WrongSignatureUser(UUID("123e4567-e89b-12d3-a456-426614174000"), "Bob Johnson")
    result3 = process_user(wrong_sig)  # Should cause error: wrong return type for get_id

    # This should work - extra methods are OK
    partial = PartiallyCompliantUser(UUID("123e4567-e89b-12d3-a456-426614174000"), "Alice Brown", "alice@example.com")
    result4 = process_user(partial)  # Should be OK

    # This should fail - CompliantUser doesn't implement ExtendedUserProtocol
    result5 = process_extended_user(compliant)  # Should cause error: missing get_email and get_roles

    return result1, result2, result3, result4, result5


# Test protocol inheritance scenarios
class BaseProtocol(Protocol):
    """Base protocol."""

    def base_method(self) -> str:
        """Base method."""
        ...


class DerivedProtocol(BaseProtocol, Protocol):
    """Derived protocol that inherits from BaseProtocol."""

    def derived_method(self) -> int:
        """Derived method."""
        ...


class IncompleteImplementation:
    """Class that only implements base protocol."""

    def base_method(self) -> str:
        return "base"


class CompleteImplementation:
    """Class that implements both base and derived protocols."""

    def base_method(self) -> str:
        return "base"

    def derived_method(self) -> int:
        return 42


def test_protocol_inheritance():
    """Test protocol inheritance scenarios."""

    incomplete = IncompleteImplementation()
    complete = CompleteImplementation()

    # This should work
    def use_base(obj: BaseProtocol) -> str:
        return obj.base_method()

    # This should work for both
    result1 = use_base(incomplete)  # Should be OK
    result2 = use_base(complete)    # Should be OK

    # This should only work for complete implementation
    def use_derived(obj: DerivedProtocol) -> str:
        return f"{obj.base_method()}: {obj.derived_method()}"

    result3 = use_derived(incomplete)  # Should cause error: missing derived_method
    result4 = use_derived(complete)    # Should be OK

    return result1, result2, result3, result4


if __name__ == "__main__":
    test_protocol_violations()
    test_protocol_inheritance()
