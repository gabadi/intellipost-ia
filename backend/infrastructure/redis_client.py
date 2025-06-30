"""
Redis client configuration and utilities.

This module provides a centralized Redis client for the application.
"""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from .config.settings import settings


class RedisClient:
    """Manages Redis connections for the application."""

    _instance: redis.Redis | None = None
    _pool: ConnectionPool | None = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get or create Redis client instance."""
        if cls._instance is None:
            cls._pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=True,
            )
            cls._instance = redis.Redis(connection_pool=cls._pool)
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """Close Redis connections."""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None


# Dependency for FastAPI
async def get_redis_client() -> redis.Redis:
    """Get Redis client for dependency injection."""
    return await RedisClient.get_client()
