"""
CSRF protection middleware for cookie-based authentication.

This module provides Cross-Site Request Forgery protection using double-submit cookies.
"""

import secrets
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.config.settings import settings


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware using double-submit cookie pattern."""

    def __init__(
        self,
        app,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        safe_methods: set[str] | None = None,
        exclude_paths: set[str] | None = None,
    ):
        """
        Initialize CSRF middleware.

        Args:
            app: FastAPI application
            cookie_name: Name of the CSRF cookie
            header_name: Name of the CSRF header
            safe_methods: HTTP methods that don't require CSRF protection
            exclude_paths: Paths to exclude from CSRF protection
        """
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.safe_methods = safe_methods or {"GET", "HEAD", "OPTIONS"}
        self.exclude_paths = exclude_paths or {
            "/health",
            "/health/ready",
            "/health/live",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
        }

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with CSRF protection."""
        # Skip CSRF check for safe methods
        if request.method in self.safe_methods:
            response = await call_next(request)
            await self._ensure_csrf_cookie(request, response)
            return response

        # Skip CSRF check for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Skip CSRF check in development mode (optional)
        if (
            settings.is_development
            and request.headers.get("X-Development-Mode") == "true"
        ):
            return await call_next(request)

        # Validate CSRF token
        if not await self._validate_csrf_token(request):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed",
            )

        # Process request
        response = await call_next(request)
        await self._ensure_csrf_cookie(request, response)

        return response

    async def _validate_csrf_token(self, request: Request) -> bool:
        """
        Validate CSRF token from cookie and header/form.

        Returns:
            True if CSRF token is valid, False otherwise
        """
        # Get token from cookie
        cookie_token = request.cookies.get(self.cookie_name)
        if not cookie_token:
            return False

        # Get token from header
        header_token = request.headers.get(self.header_name)

        # If no header token, check form data for web forms
        if not header_token and request.headers.get("content-type", "").startswith(
            "application/x-www-form-urlencoded"
        ):
            form = await request.form()
            header_token = form.get("csrf_token")

        if not header_token:
            return False

        # Compare tokens (constant-time comparison)
        return secrets.compare_digest(cookie_token, header_token)

    async def _ensure_csrf_cookie(self, request: Request, response: Response) -> None:
        """Ensure CSRF cookie is set on response."""
        # Check if cookie already exists
        if self.cookie_name not in request.cookies:
            # Generate new CSRF token
            csrf_token = secrets.token_urlsafe(32)

            # Set cookie
            response.set_cookie(
                key=self.cookie_name,
                value=csrf_token,
                httponly=False,  # Must be readable by JavaScript
                secure=settings.is_production,
                samesite="strict" if settings.is_production else "lax",
                max_age=86400,  # 24 hours
            )

            # Also add token to response header for easy access
            response.headers[self.header_name] = csrf_token
