"""
User repository implementation using SQLAlchemy.

This module provides the concrete implementation of the UserRepositoryProtocol
using SQLAlchemy for database operations.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.domain.exceptions import (
    RepositoryError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from modules.user.domain.user import User
from modules.user.domain.user_status import UserStatus

from .models import UserModel


class UserRepository:
    """
    SQLAlchemy implementation of UserRepositoryProtocol.

    Provides data persistence operations for User entities using PostgreSQL.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, user: User) -> User:
        """
        Create a new user in the database.

        Args:
            user: User entity to create

        Returns:
            User: Created user entity

        Raises:
            UserAlreadyExistsError: If user with email already exists
            RepositoryError: If database operation fails
        """
        try:
            # Create SQLAlchemy model from domain entity
            user_model = UserModel(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                first_name=user.first_name,
                last_name=user.last_name,
                status=user.status.value,
                ml_user_id=user.ml_user_id,
                ml_access_token=user.ml_access_token,
                ml_refresh_token=user.ml_refresh_token,
                ml_token_expires_at=user.ml_token_expires_at,
                default_ml_site=user.default_ml_site,
                auto_publish=user.auto_publish,
                ai_confidence_threshold=user.ai_confidence_threshold,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
                email_verified_at=user.email_verified_at,
            )

            self.session.add(user_model)
            await self.session.commit()
            await self.session.refresh(user_model)

            return self._model_to_entity(user_model)

        except IntegrityError as e:
            await self.session.rollback()
            if "email" in str(e.orig):
                raise UserAlreadyExistsError(user.email)
            raise RepositoryError("Failed to create user", e)
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError("Failed to create user", e)

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieve user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            User | None: User entity if found, None otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            return self._model_to_entity(user_model) if user_model else None

        except Exception as e:
            raise RepositoryError("Failed to retrieve user by ID", e)

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve user by email address.

        Args:
            email: User's email address

        Returns:
            User | None: User entity if found, None otherwise

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            return self._model_to_entity(user_model) if user_model else None

        except Exception as e:
            raise RepositoryError("Failed to retrieve user by email", e)

    async def update(self, user: User) -> User:
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
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(
                    email=user.email,
                    password_hash=user.password_hash,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    status=user.status.value,
                    ml_user_id=user.ml_user_id,
                    ml_access_token=user.ml_access_token,
                    ml_refresh_token=user.ml_refresh_token,
                    ml_token_expires_at=user.ml_token_expires_at,
                    default_ml_site=user.default_ml_site,
                    auto_publish=user.auto_publish,
                    ai_confidence_threshold=user.ai_confidence_threshold,
                    updated_at=user.updated_at,
                    last_login_at=user.last_login_at,
                    email_verified_at=user.email_verified_at,
                )
                .returning(UserModel)
            )

            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                raise UserNotFoundError(str(user.id))

            await self.session.commit()
            return self._model_to_entity(user_model)

        except UserNotFoundError:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError("Failed to update user", e)

    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: User's unique identifier

        Returns:
            bool: True if user was deleted, False if not found

        Raises:
            RepositoryError: If database operation fails
        """
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                return False

            await self.session.delete(user_model)
            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            raise RepositoryError("Failed to delete user", e)

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
        try:
            stmt = select(UserModel.id).where(UserModel.email == email)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            raise RepositoryError("Failed to check email existence", e)

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp.

        Args:
            user_id: User's unique identifier

        Raises:
            UserNotFoundError: If user doesn't exist
            RepositoryError: If database operation fails
        """
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(last_login_at=datetime.utcnow())
            )

            result = await self.session.execute(stmt)

            if result.rowcount == 0:
                raise UserNotFoundError(str(user_id))

            await self.session.commit()

        except UserNotFoundError:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError("Failed to update last login", e)

    def _model_to_entity(self, model: UserModel) -> User:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy user model

        Returns:
            User: Domain entity
        """
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            first_name=model.first_name,
            last_name=model.last_name,
            status=UserStatus(model.status),
            ml_user_id=model.ml_user_id,
            ml_access_token=model.ml_access_token,
            ml_refresh_token=model.ml_refresh_token,
            ml_token_expires_at=model.ml_token_expires_at,
            default_ml_site=model.default_ml_site,
            auto_publish=model.auto_publish,
            ai_confidence_threshold=model.ai_confidence_threshold,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
            email_verified_at=model.email_verified_at,
        )
