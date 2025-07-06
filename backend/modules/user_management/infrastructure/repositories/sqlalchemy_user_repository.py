"""
SQLAlchemy implementation of UserRepositoryProtocol.

This module provides PostgreSQL persistence for User entities using SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user_management.domain.entities.user import User
from modules.user_management.infrastructure.models.user_model import UserModel


class SQLAlchemyUserRepository:
    """SQLAlchemy implementation of UserRepositoryProtocol."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user."""
        user_model = UserModel.from_domain(user)
        self.session.add(user_model)
        await self.session.flush()
        await self.session.refresh(user_model)
        return user_model.to_domain()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def update(self, user: User) -> User:
        """Update an existing user."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one()

        user_model.update_from_domain(user)
        await self.session.flush()
        await self.session.refresh(user_model)
        return user_model.to_domain()

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model:
            await self.session.delete(user_model)
            await self.session.flush()
            return True
        return False
