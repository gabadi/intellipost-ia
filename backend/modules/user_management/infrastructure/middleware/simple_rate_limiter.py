"""
Simple decorator-based rate limiter for authentication endpoints.

This module provides basic rate limiting functionality using a decorator approach.
"""

import time
from collections import defaultdict, deque
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import HTTPException, Request, status

from infrastructure.config.logging import get_structured_logger

logger = get_structured_logger("rate_limiter")


class SimpleRateLimiter:
    """
    Simple in-memory rate limiter using sliding window.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps by IP
        self._request_history: dict[str, deque[float]] = defaultdict(lambda: deque())

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for the given identifier.

        Args:
            identifier: Unique identifier (typically IP address)

        Returns:
            True if request is allowed, False if rate limited
        """
        current_time = time.time()

        # Clean old entries from request history
        self._cleanup_old_requests(identifier, current_time)

        # Get current request count for this identifier
        request_history = self._request_history[identifier]

        # Check if we're within rate limit
        if len(request_history) < self.max_requests:
            # Add new request timestamp
            request_history.append(current_time)

            logger.debug(
                "Rate limit check passed",
                identifier=identifier,
                current_requests=len(request_history),
                max_requests=self.max_requests,
            )

            return True
        else:
            # Rate limit exceeded
            logger.security_event(
                "rate_limit_exceeded",
                severity="medium",
                identifier=identifier,
                current_requests=len(request_history),
                max_requests=self.max_requests,
            )

            return False

    def _cleanup_old_requests(self, identifier: str, current_time: float) -> None:
        """
        Clean up old request timestamps outside the current window.
        """
        request_history = self._request_history[identifier]
        window_start = current_time - self.window_seconds

        # Remove requests older than the current window
        while request_history and request_history[0] < window_start:
            request_history.popleft()


# Global rate limiter instance
auth_rate_limiter = SimpleRateLimiter(max_requests=5, window_seconds=60)


def rate_limit_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to apply rate limiting to authentication endpoints.

    Args:
        func: The endpoint function to rate limit

    Returns:
        Decorated function with rate limiting
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Extract the Request object from kwargs (FastAPI dependency injection)
        request = kwargs.get("http_request")

        if request is None:
            # Look for it in args as well
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is None:
            # If no request found, skip rate limiting
            logger.warning("No request object found for rate limiting")
            return await func(*args, **kwargs)

        # Get client IP
        client_ip = _get_client_ip(request)

        # Check rate limit
        if not auth_rate_limiter.is_allowed(client_ip):
            logger.security_event(
                "auth_rate_limit_blocked",
                severity="high",
                client_ip=client_ip,
                path=request.url.path,
                method=request.method,
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts. Please try again later.",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(auth_rate_limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Call the original function
        return await func(*args, **kwargs)

    return wrapper


def _get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    """
    # Check common proxy headers for real IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fallback to direct client IP
    if request.client:
        return request.client.host

    return "unknown"
