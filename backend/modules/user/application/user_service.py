"""
User service implementation.

This module provides the concrete implementation of user operations,
handling user creation and management within the user domain.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from modules.user.domain.exceptions import UserAlreadyExistsError
from modules.user.domain.ports.user_repository_protocol import UserRepositoryProtocol
from modules.user.domain.protocols import CreateUserProtocol
from modules.user.domain.user import User


class UserService:
    """
    User service implementation.

    Handles user creation and management operations within the user domain.
    This service is responsible for user entity creation and business logic.
    """

    def __init__(self, user_repository: UserRepositoryProtocol) -> None:
        """
        Initialize user service with dependencies.

        Args:
            user_repository: Repository for user data operations
        """
        self.user_repository = user_repository

    async def create_user(self, user_data: CreateUserProtocol) -> User:
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
        # Validate email doesn't already exist
        if await self.user_repository.email_exists(user_data.email):
            raise UserAlreadyExistsError(
                f"User with email {user_data.email} already exists"
            )

        # Create user entity with proper timestamps
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email=user_data.email.lower().strip(),
            password_hash=user_data.password_hash,
            first_name=user_data.first_name.strip() if user_data.first_name else None,
            last_name=user_data.last_name.strip() if user_data.last_name else None,
            status=user_data.status,
            created_at=now,
            updated_at=now,
        )

        # Save user to repository
        created_user = await self.user_repository.create(user)
        return created_user

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User | None: User entity if found, None otherwise
        """
        return await self.user_repository.get_by_email(email.lower().strip())

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User | None: User entity if found, None otherwise
        """
        return await self.user_repository.get_by_id(user_id)
