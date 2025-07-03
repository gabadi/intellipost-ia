"""
User domain service for user management operations.

This module contains pure business logic for user profile and account management.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from modules.user_management.domain.entities.user import User
from modules.user_management.domain.exceptions import OperationNotAllowedError
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)


class UserService:
    """Domain service for user account and profile management."""

    def __init__(self, user_repository: UserRepositoryProtocol):
        self._user_repository = user_repository

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        return await self._user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        return await self._user_repository.get_by_email(email.lower().strip())

    async def update_user_profile(
        self,
        user_id: UUID,
        first_name: str | None = None,
        last_name: str | None = None,
        auto_publish: bool | None = None,
        ai_confidence_threshold: str | None = None,
        default_ml_site: str | None = None,
    ) -> User | None:
        """Update user profile information."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return None

        user.update_profile(
            first_name=first_name,
            last_name=last_name,
            auto_publish=auto_publish,
            ai_confidence_threshold=ai_confidence_threshold,
            default_ml_site=default_ml_site,
        )

        return await self._user_repository.update(user)

    async def activate_user(self, user_id: UUID) -> bool:
        """Activate user account."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return False

        user.activate()
        await self._user_repository.update(user)
        return True

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return False

        user.deactivate()
        await self._user_repository.update(user)
        return True

    async def suspend_user(self, user_id: UUID) -> bool:
        """Suspend user account."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return False

        user.suspend()
        await self._user_repository.update(user)
        return True

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user account permanently."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return False

        # Business rule: Only allow deletion of inactive users
        if user.is_active:
            raise OperationNotAllowedError(
                "delete_user", "Cannot delete active user account"
            )

        return await self._user_repository.delete(user_id)

    async def connect_mercadolibre(
        self,
        user_id: UUID,
        ml_user_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
    ) -> User | None:
        """Connect user to MercadoLibre account."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return None

        user.ml_user_id = ml_user_id
        user.update_ml_tokens(access_token, refresh_token, expires_at)

        return await self._user_repository.update(user)

    async def disconnect_mercadolibre(self, user_id: UUID) -> User | None:
        """Disconnect user from MercadoLibre account."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return None

        user.disconnect_ml()

        return await self._user_repository.update(user)

    async def refresh_mercadolibre_tokens(
        self,
        user_id: UUID,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
    ) -> User | None:
        """Refresh MercadoLibre authentication tokens."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return None

        user.update_ml_tokens(access_token, refresh_token, expires_at)

        return await self._user_repository.update(user)

    async def get_user_statistics(self, user_id: UUID) -> dict[str, Any] | None:
        """Get user account statistics and summary."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return None

        return {
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "status": user.status.value,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "is_ml_connected": user.is_ml_connected,
            "account_age_days": (datetime.now(UTC) - user.created_at).days,
            "last_login": user.last_login_at.isoformat()
            if user.last_login_at
            else None,
            "failed_login_attempts": user.failed_login_attempts,
            "ml_site": user.default_ml_site,
            "auto_publish_enabled": user.auto_publish,
            "ai_confidence_threshold": user.ai_confidence_threshold,
        }
