"""
Test with lenient pyright configuration.
"""

from typing import Protocol, TypeVar, Generic, Any, Optional
from uuid import UUID


# Simple protocol test
class UserProtocol(Protocol):
    def get_name(self) -> str: ...
    def get_id(self) -> UUID: ...


class IncompleteUser:
    def get_name(self) -> str:
        return "test"
    # Missing get_id method


def use_user(user: UserProtocol) -> str:
    return f"User: {user.get_name()}"


# This should cause an error
incomplete = IncompleteUser()
result = use_user(incomplete)  # Protocol violation


# Generic test with wrong signature
T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value


# This should cause an error
int_container = Container(42)
wrong_value: str = int_container.get()  # Type mismatch
