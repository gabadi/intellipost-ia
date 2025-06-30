"""
Token blacklist service using Redis.

This module provides functionality to blacklist tokens for immediate revocation.
"""

import hashlib
from datetime import datetime

from infrastructure.config.settings import settings
from infrastructure.redis_client import RedisClient


class TokenBlacklistService:
    """Manages token blacklisting using Redis."""

    def __init__(self):
        """Initialize the token blacklist service."""
        self.key_prefix = "token_blacklist"
        self.user_tokens_prefix = "user_tokens"

    async def blacklist_token(
        self,
        token: str,
        token_type: str = "access",
        expiry_time: datetime | None = None,
    ) -> None:
        """
        Add a token to the blacklist.

        Args:
            token: The token to blacklist
            token_type: Type of token (access or refresh)
            expiry_time: When the token expires (for TTL calculation)
        """
        redis_client = await RedisClient.get_client()

        # Hash the token for storage
        token_hash = self._hash_token(token)
        key = f"{self.key_prefix}:{token_type}:{token_hash}"

        # Calculate TTL based on token expiry
        if expiry_time:
            ttl = int((expiry_time - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await redis_client.setex(key, ttl, "1")
        else:
            # Default TTL based on token type
            if token_type == "access":
                ttl = settings.jwt_access_token_expire_minutes * 60
            else:
                ttl = settings.jwt_refresh_token_expire_days * 24 * 60 * 60
            await redis_client.setex(key, ttl, "1")

    async def is_token_blacklisted(
        self, token: str, token_type: str = "access"
    ) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: The token to check
            token_type: Type of token (access or refresh)

        Returns:
            True if token is blacklisted, False otherwise
        """
        redis_client = await RedisClient.get_client()

        token_hash = self._hash_token(token)
        key = f"{self.key_prefix}:{token_type}:{token_hash}"

        return await redis_client.exists(key) > 0

    async def blacklist_all_user_tokens(self, user_id: str) -> None:
        """
        Blacklist all tokens for a user (used for logout all sessions).

        Args:
            user_id: The user ID whose tokens should be blacklisted
        """
        redis_client = await RedisClient.get_client()

        # Get all tokens for the user
        pattern = f"{self.user_tokens_prefix}:{user_id}:*"
        cursor = 0

        while True:
            cursor, keys = await redis_client.scan(cursor, match=pattern, count=100)

            for key in keys:
                token_info = await redis_client.get(key)
                if token_info:
                    # Blacklist the token
                    await self.blacklist_token(token_info, "refresh")
                    # Delete the tracking key
                    await redis_client.delete(key)

            if cursor == 0:
                break

    async def track_user_token(
        self, user_id: str, token: str, token_type: str = "refresh"
    ) -> None:
        """
        Track a token for a user (for bulk revocation).

        Args:
            user_id: The user ID
            token: The token to track
            token_type: Type of token
        """
        redis_client = await RedisClient.get_client()

        # Store token reference for user
        token_hash = self._hash_token(token)
        key = f"{self.user_tokens_prefix}:{user_id}:{token_type}:{token_hash}"

        # Store with TTL matching token expiry
        if token_type == "refresh":
            ttl = settings.jwt_refresh_token_expire_days * 24 * 60 * 60
        else:
            ttl = settings.jwt_access_token_expire_minutes * 60

        await redis_client.setex(key, ttl, token)

    async def remove_user_token(
        self, user_id: str, token: str, token_type: str = "refresh"
    ) -> None:
        """
        Remove a tracked token for a user.

        Args:
            user_id: The user ID
            token: The token to remove
            token_type: Type of token
        """
        redis_client = await RedisClient.get_client()

        token_hash = self._hash_token(token)
        key = f"{self.user_tokens_prefix}:{user_id}:{token_type}:{token_hash}"

        await redis_client.delete(key)

    def _hash_token(self, token: str) -> str:
        """Hash a token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()


# Global instance
token_blacklist = TokenBlacklistService()
