"""
Security middleware for FastAPI application.

This module provides security headers, rate limiting, and other
security measures for the IntelliPost AI backend.
"""

import time
from collections import defaultdict, deque
from typing import Any

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=()"
        )

        # Content Security Policy (basic policy for API)
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none';"
        )

        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware for authentication endpoints."""

    def __init__(
        self, app: Any, requests_per_minute: int = 60, auth_requests_per_minute: int = 5
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.auth_requests_per_minute = auth_requests_per_minute
        self.request_times: dict[str, deque] = defaultdict(deque)
        self.auth_request_times: dict[str, deque] = defaultdict(deque)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, considering proxy headers."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str, is_auth_endpoint: bool) -> bool:
        """Check if client is rate limited."""
        current_time = time.time()

        if is_auth_endpoint:
            # More restrictive rate limiting for auth endpoints
            request_times = self.auth_request_times[client_ip]
            limit = self.auth_requests_per_minute
        else:
            request_times = self.request_times[client_ip]
            limit = self.requests_per_minute

        # Remove requests older than 1 minute
        cutoff_time = current_time - 60
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()

        # Check if limit exceeded
        if len(request_times) >= limit:
            return True

        # Add current request
        request_times.append(current_time)
        return False

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = self._get_client_ip(request)
        is_auth_endpoint = request.url.path.startswith("/auth/")

        if self._is_rate_limited(client_ip, is_auth_endpoint):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error_code": "RATE_LIMITED",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60,
                },
            )

        return await call_next(request)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for additional request validation and security checks."""

    def __init__(self, app: Any, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error_code": "REQUEST_TOO_LARGE",
                    "message": f"Request size exceeds maximum allowed size of {self.max_request_size} bytes",
                },
            )

        # Basic header validation
        user_agent = request.headers.get("user-agent", "")
        if len(user_agent) > 500:  # Unusually long user agent
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_HEADERS",
                    "message": "Invalid request headers",
                },
            )

        # Check for suspicious paths
        suspicious_patterns = [
            "../",
            "..\\",
            "%2e%2e",
            "%2e%2e%2f",
            "%2e%2e%5c",
            "<script",
            "javascript:",
            "data:",
            "wp-admin",
            "admin",
            ".env",
            ".git",
        ]

        path = request.url.path.lower()
        if any(pattern in path for pattern in suspicious_patterns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_PATH",
                    "message": "Invalid request path",
                },
            )

        return await call_next(request)
