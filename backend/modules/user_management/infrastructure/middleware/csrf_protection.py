"""
CSRF Protection middleware for MercadoLibre OAuth endpoints.

This module provides CSRF protection specifically for OAuth flows
as required by the security specifications.
"""

import hashlib
import hmac
import secrets
import time

from fastapi import HTTPException, Request, status


class CSRFProtection:
    """
    CSRF protection for OAuth endpoints.

    Implements secure state parameter generation and validation
    for OAuth 2.0 flows as required by the story specifications.
    """

    def __init__(self, secret_key: str | None = None, expiry_seconds: int = 300):
        """
        Initialize CSRF protection.

        Args:
            secret_key: Secret key for HMAC signing. If None, generates a random key.
            expiry_seconds: How long state parameters are valid (default 5 minutes)
        """
        self._secret_key = (secret_key or secrets.token_urlsafe(32)).encode("utf-8")
        self._expiry_seconds = expiry_seconds

    def generate_state_token(self, user_id: str, additional_data: str = "") -> str:
        """
        Generate a secure state token for CSRF protection.

        Args:
            user_id: User ID to bind the token to
            additional_data: Additional data to include in the token

        Returns:
            Secure state token
        """
        # Create timestamp
        timestamp = str(int(time.time()))

        # Create payload
        payload = f"{user_id}:{timestamp}:{additional_data}"

        # Create HMAC signature
        signature = hmac.new(
            self._secret_key, payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Combine payload and signature
        token = f"{payload}:{signature}"

        # Base64 encode for safe URL transmission
        import base64

        return (
            base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8").rstrip("=")
        )

    def validate_state_token(
        self, token: str, user_id: str, additional_data: str = ""
    ) -> bool:
        """
        Validate a state token for CSRF protection.

        Args:
            token: State token to validate
            user_id: Expected user ID
            additional_data: Expected additional data

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Base64 decode
            import base64

            # Add padding if needed
            padded_token = token + "=" * (4 - len(token) % 4)
            decoded_token = base64.urlsafe_b64decode(padded_token).decode("utf-8")

            # Split token
            parts = decoded_token.split(":")
            if len(parts) != 4:
                return False

            token_user_id, timestamp_str, token_additional_data, signature = parts

            # Validate user ID
            if token_user_id != user_id:
                return False

            # Validate additional data
            if token_additional_data != additional_data:
                return False

            # Validate timestamp (not expired)
            try:
                timestamp = int(timestamp_str)
                current_time = int(time.time())
                if current_time - timestamp > self._expiry_seconds:
                    return False
            except ValueError:
                return False

            # Validate signature
            expected_payload = (
                f"{token_user_id}:{timestamp_str}:{token_additional_data}"
            )
            expected_signature = hmac.new(
                self._secret_key, expected_payload.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            # Use constant time comparison to prevent timing attacks
            return hmac.compare_digest(signature, expected_signature)

        except Exception:
            return False

    def validate_request_state(self, request: Request, user_id: str) -> None:
        """
        Validate CSRF state from request.

        Args:
            request: FastAPI request object
            user_id: Current user ID

        Raises:
            HTTPException: If state validation fails
        """
        # Get state from request body or query parameters
        state = None

        # Try to get from request body if it's JSON
        # Note: request.json() returns a coroutine, so we'll skip body parsing for now
        # and only use query parameters for state validation

        # Try to get from query parameters
        if not state:
            state = request.query_params.get("state")

        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "csrf_token_missing",
                    "error_description": "CSRF state parameter is required",
                },
            )

        if not self.validate_state_token(state, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "csrf_token_invalid",
                    "error_description": "Invalid or expired CSRF state parameter",
                },
            )

    def create_secure_state(self, user_id: str, redirect_uri: str = "") -> str:
        """
        Create a secure state parameter for OAuth flow.

        Args:
            user_id: User ID
            redirect_uri: OAuth redirect URI

        Returns:
            Secure state parameter
        """
        return self.generate_state_token(user_id, redirect_uri)

    def get_request_fingerprint(self, request: Request) -> str:
        """
        Get a fingerprint of the request for additional security.

        Args:
            request: FastAPI request object

        Returns:
            Request fingerprint
        """
        # Create fingerprint from user agent and other headers
        user_agent = request.headers.get("user-agent", "")
        accept_language = request.headers.get("accept-language", "")

        fingerprint_data = f"{user_agent}:{accept_language}"
        return hashlib.sha256(fingerprint_data.encode("utf-8")).hexdigest()[:16]


# Global CSRF protection instance
_csrf_protection: CSRFProtection | None = None


def get_csrf_protection() -> CSRFProtection:
    """Get or create global CSRF protection instance."""
    global _csrf_protection

    if _csrf_protection is None:
        import os

        secret_key = os.getenv("CSRF_SECRET_KEY")
        _csrf_protection = CSRFProtection(secret_key)

    return _csrf_protection


async def validate_csrf_token(request: Request, user_id: str) -> None:
    """
    Dependency for validating CSRF tokens in OAuth endpoints.

    Args:
        request: FastAPI request object
        user_id: Current user ID

    Raises:
        HTTPException: If CSRF validation fails
    """
    csrf_protection = get_csrf_protection()
    csrf_protection.validate_request_state(request, user_id)


def create_oauth_state(user_id: str, redirect_uri: str = "") -> str:
    """
    Create a secure OAuth state parameter.

    Args:
        user_id: User ID
        redirect_uri: OAuth redirect URI

    Returns:
        Secure state parameter
    """
    csrf_protection = get_csrf_protection()
    return csrf_protection.create_secure_state(user_id, redirect_uri)


def validate_oauth_state(state: str, user_id: str, redirect_uri: str = "") -> bool:
    """
    Validate an OAuth state parameter.

    Args:
        state: State parameter to validate
        user_id: Expected user ID
        redirect_uri: Expected redirect URI

    Returns:
        True if state is valid, False otherwise
    """
    csrf_protection = get_csrf_protection()
    return csrf_protection.validate_state_token(state, user_id, redirect_uri)
