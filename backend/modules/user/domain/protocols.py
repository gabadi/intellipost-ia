"""
User domain protocols.

This module contains protocol definitions for the user domain,
used for communication with other modules while maintaining clean boundaries.
"""

from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from .user_status import UserStatus

if TYPE_CHECKING:
    from .user import User


class CreateUserProtocol(Protocol):
    """
    Protocol defining the data needed to create a new user.

    This protocol allows other modules to request user creation
    without depending on the user domain implementation details.
    """

    email: str
    password_hash: str
    first_name: str | None
    last_name: str | None
    status: UserStatus


class UserServiceProtocol(Protocol):
    """
    Protocol defining the interface for user service operations.

    This protocol allows other modules to interact with user operations
    without depending on the user application layer implementation.
    """

    async def create_user(self, user_data: CreateUserProtocol) -> "User":
        """
        Create a new user with the provided data.

        Args:
            user_data: User creation data

        Returns:
            User: The created user entity

        Raises:
            UserAlreadyExistsError: If user with email already exists
            ValueError: If user data is invalid
        """
        ...

    async def get_user_by_email(self, email: str) -> "User | None":
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User | None: User entity if found, None otherwise
        """
        ...

    async def get_user_by_id(self, user_id: UUID) -> "User | None":
        """
        Get user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User | None: User entity if found, None otherwise
        """
        ...
