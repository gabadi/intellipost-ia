"""
Distributed rate limiting middleware using Redis.

This module provides request rate limiting across multiple application instances.
"""

import time
from collections.abc import Awaitable, Callable

import redis
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.redis_client import RedisClient


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Distributed rate limiting middleware using Redis."""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        key_prefix: str = "rate_limit",
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            burst_size: Maximum burst requests allowed
            key_prefix: Redis key prefix for rate limit data
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.key_prefix = key_prefix
        self.window_seconds = 60  # 1 minute window

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/ready", "/health/live"]:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        redis_client = await RedisClient.get_client()
        is_allowed = await self._check_rate_limit(redis_client, client_ip)

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        await self._add_rate_limit_headers(redis_client, client_ip, response)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check X-Forwarded-For header for proxy scenarios
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"

    async def _check_rate_limit(
        self, redis_client: redis.Redis, client_ip: str
    ) -> bool:
        """
        Check if request is within rate limit using token bucket algorithm.

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        key = f"{self.key_prefix}:{client_ip}"

        # Use Redis pipeline for atomic operations
        async with redis_client.pipeline() as pipe:
            # Get current bucket state
            bucket_data = await redis_client.hgetall(key)

            if not bucket_data:
                # Initialize new bucket
                tokens = self.burst_size
                last_refill = now
            else:
                # Calculate tokens to add based on time passed
                tokens = float(bucket_data.get("tokens", self.burst_size))
                last_refill = float(bucket_data.get("last_refill", now))

                # Refill tokens based on time passed
                time_passed = now - last_refill
                tokens_to_add = (
                    time_passed / self.window_seconds
                ) * self.requests_per_minute
                tokens = min(self.burst_size, tokens + tokens_to_add)
                last_refill = now

            # Check if we have tokens available
            if tokens < 1:
                return False

            # Consume a token
            tokens -= 1

            # Update bucket state
            pipe.multi()
            pipe.hset(
                key, mapping={"tokens": str(tokens), "last_refill": str(last_refill)}
            )
            pipe.expire(
                key, self.window_seconds * 2
            )  # Expire after 2 windows of inactivity
            await pipe.execute()

            return True

    async def _add_rate_limit_headers(
        self, redis_client: redis.Redis, client_ip: str, response: Response
    ) -> None:
        """Add rate limit information headers to response."""
        key = f"{self.key_prefix}:{client_ip}"
        bucket_data = await redis_client.hgetall(key)

        if bucket_data:
            tokens = float(bucket_data.get("tokens", self.burst_size))
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(int(tokens))
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time()) + self.window_seconds
            )
