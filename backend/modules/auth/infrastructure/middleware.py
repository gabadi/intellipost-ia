"""
Authentication middleware for FastAPI.

This module provides authentication middleware and dependencies
for protecting API endpoints with JWT tokens.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from modules.auth.api.auth_service_protocol import AuthenticationServiceProtocol
from modules.auth.domain.models import AuthenticatedUser

# HTTP Bearer security scheme for extracting tokens
security = HTTPBearer(auto_error=False)


class AuthenticationMiddleware:
    """Authentication middleware for FastAPI dependency injection."""

    def __init__(self, auth_service: AuthenticationServiceProtocol) -> None:
        """
        Initialize middleware with authentication service.

        Args:
            auth_service: Authentication service implementation
        """
        self.auth_service = auth_service

    async def get_current_user(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    ) -> AuthenticatedUser:
        """
        Get current authenticated user from JWT token.

        Args:
            credentials: HTTP authorization credentials

        Returns:
            AuthenticatedUser: Current authenticated user

        Raises:
            HTTPException: If token is missing, invalid, or expired
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials were not provided",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            return await self.auth_service.validate_token(token)
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    async def get_current_active_user(
        self,
        current_user: Annotated[AuthenticatedUser, Depends(lambda: None)],
    ) -> AuthenticatedUser:
        """
        Get current active user, ensuring account is active.

        Args:
            current_user: Current authenticated user

        Returns:
            AuthenticatedUser: Current active user

        Raises:
            HTTPException: If user account is not active
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
            )

        return current_user

    async def get_optional_current_user(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    ) -> AuthenticatedUser | None:
        """
        Get current user if authenticated, None otherwise.

        This is useful for endpoints that have optional authentication.

        Args:
            credentials: HTTP authorization credentials

        Returns:
            Optional[AuthenticatedUser]: Current user if authenticated, None otherwise
        """
        if not credentials or not credentials.credentials:
            return None

        try:
            return await self.auth_service.validate_token(credentials.credentials)
        except JWTError:
            return None


def create_auth_dependencies(auth_service: AuthenticationServiceProtocol):
    """
    Create authentication dependency functions for FastAPI.

    Args:
        auth_service: Authentication service implementation

    Returns:
        Tuple of dependency functions
    """
    middleware = AuthenticationMiddleware(auth_service)

    async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    ) -> AuthenticatedUser:
        """Dependency to get current authenticated user."""
        return await middleware.get_current_user(credentials)

    async def get_current_active_user(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AuthenticatedUser:
        """Dependency to get current active user."""
        return await middleware.get_current_active_user(current_user)

    async def get_optional_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    ) -> AuthenticatedUser | None:
        """Dependency to get optional current user."""
        return await middleware.get_optional_current_user(credentials)

    return get_current_user, get_current_active_user, get_optional_current_user


# Type aliases for dependency injection
CurrentUser = Annotated[AuthenticatedUser, Depends(lambda: None)]
CurrentActiveUser = Annotated[AuthenticatedUser, Depends(lambda: None)]
OptionalCurrentUser = Annotated[AuthenticatedUser | None, Depends(lambda: None)]
