"""
User MercadoLibre integration logic.

This module contains methods for managing MercadoLibre integration.
"""

from datetime import datetime

from .user_core import UserCore


class UserMLIntegration:
    """MercadoLibre integration methods for user entities."""

    @staticmethod
    def is_ml_connected(user: UserCore) -> bool:
        """Check if user has valid MercadoLibre connection."""
        return (
            user.ml_user_id is not None
            and user.ml_access_token is not None
            and user.ml_token_expires_at is not None
            and user.ml_token_expires_at > datetime.utcnow()
        )

    @staticmethod
    def update_ml_tokens(
        user: UserCore, access_token: str, refresh_token: str, expires_at: datetime
    ) -> None:
        """Update MercadoLibre authentication tokens."""
        user.ml_access_token = access_token
        user.ml_refresh_token = refresh_token
        user.ml_token_expires_at = expires_at
        user.updated_at = datetime.utcnow()
