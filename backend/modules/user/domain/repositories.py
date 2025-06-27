"""
User repository protocol definitions.

This module contains the user repository Protocol interface following
hexagonal architecture principles.
"""

from typing import Protocol
from uuid import UUID

from .user import User


class UserRepository(Protocol):
    """
    User repository protocol interface.

    This protocol defines the contract for user data persistence
    operations following the hexagonal architecture pattern.
    """

    async def create_user(self, user: User) -> User:
        """
        Create a new user in the database.

        Args:
            user: User entity to create

        Returns:
            User: Created user entity with populated ID

        Raises:
            UserAlreadyExistsError: If user with email already exists
            RepositoryError: If database operation fails
        """
        ...

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve user by email address.

        Args:
            email: User's email address

        Returns:
            Optional[User]: User entity if found, None otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        ...

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieve user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            Optional[User]: User entity if found, None otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        ...

    async def update_user(self, user: User) -> User:
        """
        Update existing user in the database.

        Args:
            user: User entity with updated data

        Returns:
            User: Updated user entity

        Raises:
            UserNotFoundError: If user doesn't exist
            RepositoryError: If database operation fails
        """
        ...

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp.

        Args:
            user_id: User's unique identifier

        Raises:
            UserNotFoundError: If user doesn't exist
            RepositoryError: If database operation fails
        """
        ...

    async def email_exists(self, email: str) -> bool:
        """
        Check if email address is already registered.

        Args:
            email: Email address to check

        Returns:
            bool: True if email exists, False otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        ...
