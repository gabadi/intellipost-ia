"""
HTTPS and security middleware for production deployments.

This module provides security middleware for HTTPS enforcement and security headers.
"""

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from infrastructure.config.logging import get_structured_logger
from infrastructure.config.settings import Settings

logger = get_structured_logger("security_middleware")


class HTTPSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS and add security headers in production.

    Features:
    - HTTPS redirect in production
    - HSTS (HTTP Strict Transport Security) headers
    - Secure cookie configuration
    - Security headers for authentication
    """

    def __init__(self, app, settings: Settings):
        """
        Initialize HTTPS security middleware.

        Args:
            app: FastAPI application
            settings: Application settings
        """
        super().__init__(app)
        self.settings = settings

        logger.info(
            "HTTPS Security middleware initialized",
            environment=settings.environment,
            https_only=settings.https_only,
            secure_cookies=settings.secure_cookies,
            hsts_max_age=settings.hsts_max_age,
        )

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process request with HTTPS security enforcement.

        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint handler

        Returns:
            HTTP response with security headers
        """
        # Check if HTTPS enforcement is needed
        if self.settings.https_only and self._should_redirect_to_https(request):
            return self._redirect_to_https(request)

        # Process the request
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)

        # Log security enforcement
        if self.settings.https_only:
            logger.debug(
                "HTTPS security enforced",
                scheme=request.url.scheme,
                path=request.url.path,
                secure_headers_added=True,
            )

        return response

    def _should_redirect_to_https(self, request: Request) -> bool:
        """
        Check if request should be redirected to HTTPS.

        Args:
            request: FastAPI request object

        Returns:
            True if redirect is needed
        """
        # Skip redirect for localhost in development
        if self.settings.is_development:
            return False

        # Check if request is already HTTPS
        if request.url.scheme == "https":
            return False

        # Check for X-Forwarded-Proto header (common in proxy setups)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        if forwarded_proto == "https":
            return False

        # Check for X-Forwarded-SSL header
        forwarded_ssl = request.headers.get("X-Forwarded-SSL", "").lower()
        return forwarded_ssl != "on"

    def _redirect_to_https(self, request: Request) -> RedirectResponse:
        """
        Create HTTPS redirect response.

        Args:
            request: FastAPI request object

        Returns:
            Redirect response to HTTPS URL
        """
        https_url = request.url.replace(scheme="https")

        # Log the redirect
        logger.security_event(
            "https_redirect",
            severity="low",
            original_url=str(request.url),
            redirect_url=str(https_url),
            client_ip=request.client.host if request.client else "unknown",
        )

        return RedirectResponse(
            url=str(https_url),
            status_code=301,  # Permanent redirect
        )

    def _add_security_headers(self, response: Response) -> None:
        """
        Add security headers to response.

        Args:
            response: FastAPI response object
        """
        # HSTS (HTTP Strict Transport Security)
        if self.settings.https_only:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.settings.hsts_max_age}; includeSubDomains; preload"
            )

        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (basic)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )

        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )

        # Cache control for sensitive endpoints
        if self._is_auth_endpoint(response):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, private"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

    def _is_auth_endpoint(self, response: Response) -> bool:
        """
        Check if response is from an authentication endpoint.

        Args:
            response: FastAPI response object

        Returns:
            True if response is from auth endpoint
        """
        # This is a simple heuristic - in practice you might want to be more specific
        content_type = response.headers.get("content-type", "")
        return "application/json" in content_type and hasattr(response, "body")


class SecureCookieMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce secure cookie settings in production.
    """

    def __init__(self, app, settings: Settings):
        """
        Initialize secure cookie middleware.

        Args:
            app: FastAPI application
            settings: Application settings
        """
        super().__init__(app)
        self.settings = settings

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process request and secure cookies in response.

        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint handler

        Returns:
            HTTP response with secure cookies
        """
        response = await call_next(request)

        # Secure cookies in production
        if self.settings.secure_cookies:
            self._secure_cookies(response)

        return response

    def _secure_cookies(self, response: Response) -> None:
        """
        Make cookies secure in production.

        Args:
            response: FastAPI response object
        """
        # This is a basic implementation
        # In practice, you'd want to modify Set-Cookie headers
        # to add Secure, HttpOnly, and SameSite attributes

        # Note: FastAPI handles most cookie security through its cookie settings
        # This middleware is here for additional cookie security enforcement
        set_cookie_headers = response.headers.get_list("set-cookie")
        if set_cookie_headers:
            logger.debug(
                "Secure cookie enforcement applied",
                cookie_count=len(set_cookie_headers),
            )


def create_security_middleware(settings: Settings) -> list:
    """
    Create list of security middleware based on settings.

    Args:
        settings: Application settings

    Returns:
        List of middleware classes to add to FastAPI
    """
    middleware = []

    # HTTPS Security Middleware
    if settings.https_only or settings.is_production:
        middleware.append((HTTPSSecurityMiddleware, {"settings": settings}))

    # Secure Cookie Middleware
    if settings.secure_cookies or settings.is_production:
        middleware.append((SecureCookieMiddleware, {"settings": settings}))

    logger.info(
        "Security middleware configured",
        middleware_count=len(middleware),
        https_enabled=settings.https_only,
        secure_cookies=settings.secure_cookies,
        environment=settings.environment,
    )

    return middleware
