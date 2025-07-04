"""
Simple in-memory rate limiter middleware for authentication endpoints.

This module provides basic rate limiting functionality to protect against brute force attacks.
For production, consider using Redis-based rate limiting for distributed systems.
"""

import time
from collections import defaultdict, deque
from datetime import UTC, datetime

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.config.logging import get_structured_logger

logger = get_structured_logger("rate_limiter")


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm.

    This implementation stores rate limiting data in memory and is suitable for MVP.
    For production use, consider implementing with Redis for distributed rate limiting.
    """

    def __init__(self, max_requests: int = 5, window_minutes: int = 1):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_minutes: Time window in minutes
        """
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        # Store tuples of (request_count, window_start_time) by IP
        self._buckets: dict[str, tuple[int, float]] = {}
        # Store request timestamps for detailed tracking
        self._request_history: dict[str, deque] = defaultdict(lambda: deque())

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

            # Log allowed request
            logger.debug(
                "Rate limit check passed",
                identifier=identifier,
                current_requests=len(request_history),
                max_requests=self.max_requests,
                window_seconds=self.window_seconds,
            )

            return True
        else:
            # Rate limit exceeded
            oldest_request = request_history[0] if request_history else current_time
            reset_time = oldest_request + self.window_seconds

            # Log rate limit exceeded
            logger.security_event(
                "rate_limit_exceeded",
                severity="medium",
                identifier=identifier,
                current_requests=len(request_history),
                max_requests=self.max_requests,
                window_seconds=self.window_seconds,
                reset_in_seconds=max(0, reset_time - current_time),
            )

            return False

    def _cleanup_old_requests(self, identifier: str, current_time: float) -> None:
        """
        Clean up old request timestamps outside the current window.

        Args:
            identifier: Request identifier
            current_time: Current timestamp
        """
        request_history = self._request_history[identifier]
        window_start = current_time - self.window_seconds

        # Remove requests older than the current window
        while request_history and request_history[0] < window_start:
            request_history.popleft()

    def get_reset_time(self, identifier: str) -> datetime | None:
        """
        Get the time when rate limit will reset for identifier.

        Args:
            identifier: Request identifier

        Returns:
            DateTime when rate limit resets, None if not rate limited
        """
        request_history = self._request_history[identifier]
        if not request_history or len(request_history) < self.max_requests:
            return None

        oldest_request = request_history[0]
        reset_timestamp = oldest_request + self.window_seconds
        return datetime.fromtimestamp(reset_timestamp, tz=UTC)

    def get_remaining_requests(self, identifier: str) -> int:
        """
        Get number of remaining requests for identifier.

        Args:
            identifier: Request identifier

        Returns:
            Number of remaining requests in current window
        """
        current_time = time.time()
        self._cleanup_old_requests(identifier, current_time)

        request_history = self._request_history[identifier]
        return max(0, self.max_requests - len(request_history))


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware specifically for authentication endpoints.

    This middleware applies rate limiting only to authentication routes
    to prevent brute force attacks while not affecting other endpoints.
    """

    def __init__(self, app, max_requests: int = 5, window_minutes: int = 1):
        """
        Initialize auth rate limit middleware.

        Args:
            app: FastAPI application
            max_requests: Maximum requests per window (default: 5)
            window_minutes: Time window in minutes (default: 1)
        """
        super().__init__(app)
        self.rate_limiter = InMemoryRateLimiter(max_requests, window_minutes)
        self.auth_paths = {
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
            "/auth/logout",
        }

        logger.info(
            "Auth rate limiter initialized",
            max_requests=max_requests,
            window_minutes=window_minutes,
            protected_paths=list(self.auth_paths),
        )

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting for auth endpoints.

        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint handler

        Returns:
            HTTP response
        """
        # Only apply rate limiting to authentication endpoints
        if not self._is_auth_endpoint(request.url.path):
            return await call_next(request)

        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Check rate limit
        if not self.rate_limiter.is_allowed(client_ip):
            reset_time = self.rate_limiter.get_reset_time(client_ip)
            reset_seconds = (
                int((reset_time - datetime.now(UTC)).total_seconds())
                if reset_time
                else 60
            )

            # Log rate limit violation
            logger.security_event(
                "auth_rate_limit_blocked",
                severity="high",
                client_ip=client_ip,
                path=request.url.path,
                method=request.method,
                reset_in_seconds=reset_seconds,
                user_agent=request.headers.get("user-agent", "unknown"),
            )

            # Return rate limit error with retry information
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many authentication attempts. Try again in {reset_seconds} seconds.",
                headers={
                    "Retry-After": str(reset_seconds),
                    "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time.timestamp()))
                    if reset_time
                    else str(int(time.time()) + 60),
                },
            )

        # Process the request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = self.rate_limiter.get_remaining_requests(client_ip)
        reset_time = self.rate_limiter.get_reset_time(client_ip)

        try:
            response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            if reset_time:
                response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))
        except Exception as e:
            # If adding headers fails, log but don't break the response
            logger.debug(
                "Failed to add rate limit headers", error=str(e), client_ip=client_ip
            )

        # Log successful auth request
        logger.debug(
            "Auth request processed",
            client_ip=client_ip,
            path=request.url.path,
            method=request.method,
            remaining_requests=remaining,
            status_code=response.status_code,
        )

        return response

    def _is_auth_endpoint(self, path: str) -> bool:
        """
        Check if the request path is an authentication endpoint.

        Args:
            path: Request path

        Returns:
            True if path is an authentication endpoint
        """
        return path in self.auth_paths

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Handles various proxy headers for accurate IP detection.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address
        """
        # Check common proxy headers for real IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        # Ultimate fallback
        return "unknown"


# Global rate limiter instance for auth endpoints
# 5 requests per minute as specified in requirements
auth_rate_limiter = AuthRateLimitMiddleware(
    app=None,  # Will be set when middleware is added to app
    max_requests=5,
    window_minutes=1,
)
