"""
Secure token storage implementation for authentication system.

This module provides secure token storage using HTTP-only cookies with proper
security headers and validation.
"""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.infrastructure.config.settings import settings


class SecureTokenStorage:
    """Secure token storage using HTTP-only cookies."""

    # Cookie names
    ACCESS_TOKEN_COOKIE = "intellipost_access_token"
    REFRESH_TOKEN_COOKIE = "intellipost_refresh_token"
    CSRF_TOKEN_COOKIE = "intellipost_csrf_token"

    # Security settings
    SECURE_FLAG = not settings.is_development  # HTTPS in production
    SAMESITE = "lax"  # Protect against CSRF
    HTTPONLY = True  # Prevent XSS access

    def __init__(self):
        """Initialize secure token storage."""
        self.csrf_secret = settings.secret_key.encode()

    def set_authentication_cookies(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
        access_token_expires_in: int,
    ) -> None:
        """
        Set secure authentication cookies.

        Args:
            response: FastAPI response object
            access_token: JWT access token
            refresh_token: JWT refresh token
            access_token_expires_in: Access token expiration in seconds
        """
        # Generate CSRF token
        csrf_token = self._generate_csrf_token()

        # Set access token cookie
        response.set_cookie(
            key=self.ACCESS_TOKEN_COOKIE,
            value=access_token,
            max_age=access_token_expires_in,
            httponly=self.HTTPONLY,
            secure=self.SECURE_FLAG,
            samesite=self.SAMESITE,
            path="/",
        )

        # Set refresh token cookie (longer expiration)
        refresh_expires = (
            settings.jwt_refresh_token_expire_days * 24 * 60 * 60
        )  # Convert to seconds
        response.set_cookie(
            key=self.REFRESH_TOKEN_COOKIE,
            value=refresh_token,
            max_age=refresh_expires,
            httponly=self.HTTPONLY,
            secure=self.SECURE_FLAG,
            samesite=self.SAMESITE,
            path="/auth",  # Restrict to auth endpoints
        )

        # Set CSRF token cookie (readable by JavaScript for forms)
        response.set_cookie(
            key=self.CSRF_TOKEN_COOKIE,
            value=csrf_token,
            max_age=access_token_expires_in,
            httponly=False,  # Accessible to JavaScript
            secure=self.SECURE_FLAG,
            samesite=self.SAMESITE,
            path="/",
        )

    def get_access_token(self, request: Request) -> str | None:
        """
        Extract access token from cookies or Authorization header.

        Args:
            request: FastAPI request object

        Returns:
            Access token if found and valid, None otherwise
        """
        # Try cookie first (more secure)
        access_token = request.cookies.get(self.ACCESS_TOKEN_COOKIE)
        if access_token:
            return access_token

        # Fallback to Authorization header for API clients
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ")[1]

        return None

    def get_refresh_token(self, request: Request) -> str | None:
        """
        Extract refresh token from cookies.

        Args:
            request: FastAPI request object

        Returns:
            Refresh token if found, None otherwise
        """
        return request.cookies.get(self.REFRESH_TOKEN_COOKIE)

    def validate_csrf_token(self, request: Request) -> bool:
        """
        Validate CSRF token for state-changing operations.

        Args:
            request: FastAPI request object

        Returns:
            True if CSRF token is valid, False otherwise
        """
        # Skip CSRF validation for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Get CSRF token from header or form data
        csrf_token = request.headers.get("X-CSRF-Token") or request.headers.get(
            "X-CSRFToken"
        )

        if not csrf_token:
            return False

        # Validate CSRF token
        return self._validate_csrf_token(csrf_token)

    def clear_authentication_cookies(self, response: Response) -> None:
        """
        Clear all authentication cookies.

        Args:
            response: FastAPI response object
        """
        # Clear access token cookie
        response.delete_cookie(
            key=self.ACCESS_TOKEN_COOKIE,
            path="/",
            secure=self.SECURE_FLAG,
            samesite=self.SAMESITE,
        )

        # Clear refresh token cookie
        response.delete_cookie(
            key=self.REFRESH_TOKEN_COOKIE,
            path="/auth",
            secure=self.SECURE_FLAG,
            samesite=self.SAMESITE,
        )

        # Clear CSRF token cookie
        response.delete_cookie(
            key=self.CSRF_TOKEN_COOKIE,
            path="/",
            secure=self.SECURE_FLAG,
            samesite=self.SAMESITE,
        )

    def _generate_csrf_token(self) -> str:
        """
        Generate secure CSRF token.

        Returns:
            CSRF token string
        """
        # Generate random token
        random_part = secrets.token_urlsafe(32)

        # Create HMAC signature
        signature = hmac.new(
            self.csrf_secret, random_part.encode(), hashlib.sha256
        ).hexdigest()

        return f"{random_part}.{signature}"

    def _validate_csrf_token(self, token: str) -> bool:
        """
        Validate CSRF token signature.

        Args:
            token: CSRF token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return False

            random_part, signature = parts

            # Verify signature
            expected_signature = hmac.new(
                self.csrf_secret, random_part.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception:
            return False


class CookieAuthenticationBearer(HTTPBearer):
    """Custom HTTPBearer that supports cookie-based authentication."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.token_storage = SecureTokenStorage()

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        """
        Extract authentication credentials from cookies or headers.

        Args:
            request: FastAPI request object

        Returns:
            HTTPAuthorizationCredentials if token found, None otherwise
        """
        # Try to get token from secure storage
        access_token = self.token_storage.get_access_token(request)

        if access_token:
            return HTTPAuthorizationCredentials(
                scheme="Bearer", credentials=access_token
            )

        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return None


def add_security_headers(response: Response) -> None:
    """
    Add security headers to response.

    Args:
        response: FastAPI response object
    """
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # HTTPS enforcement (in production)
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions policy
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), "
        "accelerometer=(), gyroscope=(), magnetometer=(), "
        "payment=(), usb=()"
    )


class TokenBlacklist:
    """Simple in-memory token blacklist for logout functionality."""

    def __init__(self):
        """Initialize token blacklist."""
        self._blacklisted_tokens: dict[str, datetime] = {}
        self._cleanup_interval = timedelta(hours=1)
        self._last_cleanup = datetime.now(UTC)

    def blacklist_token(self, token_jti: str, expires_at: datetime) -> None:
        """
        Add token to blacklist.

        Args:
            token_jti: JWT ID (jti claim)
            expires_at: Token expiration time
        """
        self._blacklisted_tokens[token_jti] = expires_at
        self._cleanup_expired_tokens()

    def is_blacklisted(self, token_jti: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token_jti: JWT ID to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        self._cleanup_expired_tokens()
        return token_jti in self._blacklisted_tokens

    def _cleanup_expired_tokens(self) -> None:
        """Remove expired tokens from blacklist."""
        now = datetime.now(UTC)

        # Only cleanup if enough time has passed
        if now - self._last_cleanup < self._cleanup_interval:
            return

        # Remove expired tokens
        expired_tokens = [
            jti
            for jti, expires_at in self._blacklisted_tokens.items()
            if expires_at <= now
        ]

        for jti in expired_tokens:
            del self._blacklisted_tokens[jti]

        self._last_cleanup = now


# Global instances
secure_token_storage = SecureTokenStorage()
cookie_auth_bearer = CookieAuthenticationBearer()
token_blacklist = TokenBlacklist()
