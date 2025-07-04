"""
SQLAlchemy user repository implementation for user management module.

This module provides user data persistence operations using SQLAlchemy.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user_management.domain.entities.user import User, UserStatus
from modules.user_management.infrastructure.models.user_model import UserModel


class UserRepository:
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            model: UserModel instance

        Returns:
            User domain entity
        """
        return User(
            id=UUID(str(model.id)),
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
            first_name=model.first_name,
            last_name=model.last_name,
            status=UserStatus(model.status),
            is_active=model.is_active,
            is_email_verified=model.is_email_verified,
            failed_login_attempts=model.failed_login_attempts,
            last_failed_login_at=model.last_failed_login_at,
            password_reset_token=model.password_reset_token,
            password_reset_expires_at=model.password_reset_expires_at,
            email_verification_token=model.email_verification_token,
            ml_user_id=model.ml_user_id,
            ml_access_token=model.ml_access_token,
            ml_refresh_token=model.ml_refresh_token,
            ml_token_expires_at=model.ml_token_expires_at,
            default_ml_site=model.default_ml_site,
            auto_publish=model.auto_publish,
            ai_confidence_threshold=model.ai_confidence_threshold,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
            email_verified_at=model.email_verified_at,
        )

    def _entity_to_model(self, entity: User) -> UserModel:
        """
        Convert domain entity to SQLAlchemy model.

        Args:
            entity: User domain entity

        Returns:
            UserModel instance
        """
        return UserModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            status=entity.status.value,
            is_email_verified=entity.is_email_verified,
            failed_login_attempts=entity.failed_login_attempts,
            last_failed_login_at=entity.last_failed_login_at,
            password_reset_token=entity.password_reset_token,
            password_reset_expires_at=entity.password_reset_expires_at,
            email_verification_token=entity.email_verification_token,
            ml_user_id=entity.ml_user_id,
            ml_access_token=entity.ml_access_token,
            ml_refresh_token=entity.ml_refresh_token,
            ml_token_expires_at=entity.ml_token_expires_at,
            default_ml_site=entity.default_ml_site,
            auto_publish=entity.auto_publish,
            ai_confidence_threshold=entity.ai_confidence_threshold,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login_at=entity.last_login_at,
            email_verified_at=entity.email_verified_at,
        )

    async def create(self, user: User) -> User:
        """
        Create a new user.

        Args:
            user: User entity to create

        Returns:
            Created user entity with any generated fields
        """
        model = self._entity_to_model(user)
        self._session.add(model)
        await self._session.flush()  # Flush to get generated ID
        await self._session.refresh(model)  # Refresh to get all fields
        return self._model_to_entity(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User entity if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: User email address

        Returns:
            User entity if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def update(self, user: User) -> User:
        """
        Update an existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user entity
        """
        # Get existing model
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"User with ID {user.id} not found")

        # Update model fields from entity
        model.email = user.email
        model.password_hash = user.password_hash
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.is_active = user.is_active
        model.status = user.status.value
        model.is_email_verified = user.is_email_verified
        model.failed_login_attempts = user.failed_login_attempts
        model.last_failed_login_at = user.last_failed_login_at
        model.password_reset_token = user.password_reset_token
        model.password_reset_expires_at = user.password_reset_expires_at
        model.email_verification_token = user.email_verification_token
        model.ml_user_id = user.ml_user_id
        model.ml_access_token = user.ml_access_token
        model.ml_refresh_token = user.ml_refresh_token
        model.ml_token_expires_at = user.ml_token_expires_at
        model.default_ml_site = user.default_ml_site
        model.auto_publish = user.auto_publish
        model.ai_confidence_threshold = user.ai_confidence_threshold
        model.updated_at = datetime.now(UTC)
        model.last_login_at = user.last_login_at
        model.email_verified_at = user.email_verified_at

        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: User UUID

        Returns:
            True if user was deleted, False if not found
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return False

        await self._session.delete(model)
        return True
