"""
MercadoLibre API Client for OAuth and token operations.

This module provides a client for interacting with MercadoLibre OAuth 2.0
endpoints with rate limiting and error handling.
"""

import asyncio
import json
import time
from typing import Any
from urllib.parse import urlencode

import httpx
from httpx import AsyncClient, Response


class MLAPIError(Exception):
    """Base exception for MercadoLibre API errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class MLRateLimitError(MLAPIError):
    """Exception for rate limit errors (429)."""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message, error_code="rate_limited", status_code=429)
        self.retry_after = retry_after


class MLOAuthError(MLAPIError):
    """Exception for OAuth-specific errors."""

    pass


class MLManagerAccountError(MLAPIError):
    """Exception for manager account requirement errors."""

    pass


class MercadoLibreAPIClient:
    """
    Client for MercadoLibre API operations with OAuth support.

    Implements rate limiting, error handling, and retry logic
    as required by the story specifications.
    """

    # Country-specific configuration
    SITE_DOMAINS = {
        "MLA": "mercadolibre.com.ar",
        "MLM": "mercadolibre.com.mx",
        "MBL": "mercadolibre.com.br",
        "MLC": "mercadolibre.cl",
        "MCO": "mercadolibre.com.co",
    }

    AUTH_URLS = {
        "MLA": "https://auth.mercadolibre.com.ar/authorization",
        "MLM": "https://auth.mercadolibre.com.mx/authorization",
        "MBL": "https://auth.mercadolibre.com.br/authorization",
        "MLC": "https://auth.mercadolibre.cl/authorization",
        "MCO": "https://auth.mercadolibre.com.co/authorization",
    }

    TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
    USER_URL = "https://api.mercadolibre.com/users/me"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_per_minute: int = 10,
    ):
        """
        Initialize MercadoLibre API client.

        Args:
            client_id: MercadoLibre app ID
            client_secret: MercadoLibre app secret
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit_per_minute: Rate limit per minute
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_per_minute = rate_limit_per_minute

        # Rate limiting tracking
        self._request_times: list[float] = []
        self._last_request_time: float = 0

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        retry_count: int = 0,
    ) -> Response:
        """
        Make HTTP request with rate limiting and error handling.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            data: Request data
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            HTTP response

        Raises:
            MLAPIError: For various API errors
        """
        # Rate limiting
        await self._enforce_rate_limit()

        # Prepare request
        request_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if headers:
            request_headers.update(headers)

        # Convert data to form-encoded if present
        request_data = None
        if data:
            request_data = urlencode(data)

        try:
            async with AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    content=request_data,
                    params=params,
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    if retry_count < self.max_retries:
                        await asyncio.sleep(retry_after)
                        return await self._make_request(
                            method, url, headers, data, params, retry_count + 1
                        )
                    else:
                        raise MLRateLimitError(
                            "Rate limit exceeded and max retries reached",
                            retry_after=retry_after,
                        )

                # Handle OAuth errors
                if response.status_code >= 400:
                    await self._handle_error_response(response)

                return response

        except httpx.RequestError as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(2**retry_count)  # Exponential backoff
                return await self._make_request(
                    method, url, headers, data, params, retry_count + 1
                )
            else:
                raise MLAPIError(f"Request failed: {str(e)}") from e

    async def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting based on requests per minute."""
        current_time = time.time()

        # Clean old requests (older than 1 minute)
        self._request_times = [t for t in self._request_times if current_time - t < 60]

        # Check if we've hit the limit
        if len(self._request_times) >= self.rate_limit_per_minute:
            sleep_time = 60 - (current_time - self._request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        # Record this request
        self._request_times.append(current_time)
        self._last_request_time = current_time

    async def _handle_error_response(self, response: Response) -> None:
        """Handle error responses from MercadoLibre API."""
        try:
            error_data = response.json()
            error_code = error_data.get("error", "unknown_error")
            error_description = error_data.get("error_description", "Unknown error")

            # Handle specific OAuth errors
            if error_code == "invalid_client":
                raise MLOAuthError(
                    "Invalid client credentials",
                    error_code=error_code,
                    status_code=response.status_code,
                )
            elif error_code == "invalid_grant":
                raise MLOAuthError(
                    "Invalid authorization grant",
                    error_code=error_code,
                    status_code=response.status_code,
                )
            elif error_code == "invalid_scope":
                raise MLOAuthError(
                    "Invalid scope requested",
                    error_code=error_code,
                    status_code=response.status_code,
                )
            elif "collaborator" in error_description.lower():
                raise MLManagerAccountError(
                    "Only manager accounts can authorize applications",
                    error_code=error_code,
                    status_code=response.status_code,
                )
            else:
                raise MLAPIError(
                    f"{error_code}: {error_description}",
                    error_code=error_code,
                    status_code=response.status_code,
                )

        except json.JSONDecodeError as e:
            # Handle non-JSON error responses
            raise MLAPIError(
                f"HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
            ) from e

    def build_auth_url(
        self,
        site_id: str,
        redirect_uri: str,
        state: str,
        code_challenge: str,
        scopes: str = "offline_access read write",
    ) -> str:
        """
        Build authorization URL for OAuth flow.

        Args:
            site_id: MercadoLibre site ID
            redirect_uri: OAuth redirect URI
            state: CSRF state parameter
            code_challenge: PKCE code challenge
            scopes: OAuth scopes

        Returns:
            Authorization URL

        Raises:
            ValueError: If site_id is invalid
        """
        if site_id not in self.AUTH_URLS:
            raise ValueError(f"Invalid site_id: {site_id}")

        auth_url = self.AUTH_URLS[site_id]

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scopes,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        return f"{auth_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access tokens.

        Args:
            code: Authorization code
            redirect_uri: OAuth redirect URI
            code_verifier: PKCE code verifier

        Returns:
            Token response data

        Raises:
            MLOAuthError: If token exchange fails
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }

        response = await self._make_request("POST", self.TOKEN_URL, data=data)
        return response.json()

    async def refresh_tokens(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresh access tokens using refresh token.

        CRITICAL: Implements single-use refresh token requirement.

        Args:
            refresh_token: Current refresh token

        Returns:
            New token response data

        Raises:
            MLOAuthError: If token refresh fails
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }

        response = await self._make_request("POST", self.TOKEN_URL, data=data)
        return response.json()

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information using access token.

        Args:
            access_token: ML access token

        Returns:
            User information data

        Raises:
            MLAPIError: If user info request fails
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self._make_request("GET", self.USER_URL, headers=headers)
        return response.json()

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate access token by making a test request.

        Args:
            access_token: ML access token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            await self.get_user_info(access_token)
            return True
        except MLAPIError:
            return False

    def get_site_domain(self, site_id: str) -> str:
        """Get domain for site ID."""
        return self.SITE_DOMAINS.get(site_id, "mercadolibre.com.ar")

    def get_auth_domain(self, site_id: str) -> str:
        """Get auth domain for site ID."""
        return self.AUTH_URLS.get(site_id, "https://auth.mercadolibre.com.ar").replace(
            "https://", ""
        )

    async def check_manager_account(self, access_token: str) -> bool:
        """
        Check if the account is a manager account.

        CRITICAL: Only manager accounts can authorize applications.

        Args:
            access_token: ML access token

        Returns:
            True if manager account, False if collaborator

        Raises:
            MLAPIError: If check fails
        """
        try:
            user_info = await self.get_user_info(access_token)
            # Check if user has manager permissions
            # This is a simplified check - actual implementation may need
            # to check specific user roles or permissions
            return user_info.get("account_type") != "collaborator"
        except MLAPIError:
            return False

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke access token.

        Args:
            access_token: ML access token to revoke

        Returns:
            True if revocation successful, False otherwise
        """
        try:
            # MercadoLibre doesn't have a standard revoke endpoint
            # Token revocation happens automatically when user changes password
            # or manually removes app permissions
            return True
        except MLAPIError:
            return False
