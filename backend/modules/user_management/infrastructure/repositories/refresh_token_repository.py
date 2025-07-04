"""
SQLAlchemy refresh token repository implementation for user management module.

This module provides refresh token data persistence operations using SQLAlchemy.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user_management.domain.entities.refresh_token import RefreshToken
from modules.user_management.infrastructure.models.user_model import RefreshTokenModel


class RefreshTokenRepository:
    """SQLAlchemy implementation of refresh token repository."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    def _model_to_entity(self, model: RefreshTokenModel) -> RefreshToken:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            model: RefreshTokenModel instance

        Returns:
            RefreshToken domain entity
        """
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
        )

    def _entity_to_model(self, entity: RefreshToken) -> RefreshTokenModel:
        """
        Convert domain entity to SQLAlchemy model.

        Args:
            entity: RefreshToken domain entity

        Returns:
            RefreshTokenModel instance
        """
        return RefreshTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
        )

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """
        Create a new refresh token.

        Args:
            refresh_token: RefreshToken entity to create

        Returns:
            Created refresh token entity with any generated fields
        """
        model = self._entity_to_model(refresh_token)
        self._session.add(model)
        await self._session.flush()  # Flush to get generated ID
        await self._session.refresh(model)  # Refresh to get all fields
        return self._model_to_entity(model)

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """
        Get refresh token by token hash.

        Args:
            token_hash: Hashed token string

        Returns:
            RefreshToken entity if found, None otherwise
        """
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        """
        Get all refresh tokens for a user.

        Args:
            user_id: User UUID

        Returns:
            List of RefreshToken entities for the user
        """
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def delete_by_token_hash(self, token_hash: str) -> bool:
        """
        Delete refresh token by token hash.

        Args:
            token_hash: Hashed token string

        Returns:
            True if token was deleted, False if not found
        """
        stmt = delete(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def delete_by_user_id(self, user_id: UUID) -> int:
        """
        Delete all refresh tokens for a user.

        Args:
            user_id: User UUID

        Returns:
            Count of deleted refresh tokens
        """
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.rowcount

    async def delete_expired(self) -> int:
        """
        Delete all expired refresh tokens.

        Returns:
            Count of deleted refresh tokens
        """
        now = datetime.now(UTC)
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.expires_at <= now)
        result = await self._session.execute(stmt)
        return result.rowcount
