"""
JWT Authentication middleware for user management module.

This module provides FastAPI dependencies for JWT token validation and user authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_database_session
from modules.user_management.domain.entities.user import User
from modules.user_management.infrastructure.repositories.user_repository import (
    UserRepository,
)
from modules.user_management.infrastructure.services.jwt_service import JWTService

# Security scheme for bearer token
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


class AuthenticationMiddleware:
    """JWT authentication middleware for FastAPI."""

    def __init__(self):
        self._jwt_service = JWTService()

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials,
        session: AsyncSession,
    ) -> User:
        """
        Get current authenticated user from JWT token.

        Args:
            credentials: HTTP bearer token credentials
            session: Database session

        Returns:
            Current authenticated user

        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            # Extract token from credentials
            token = credentials.credentials

            # Verify token and extract user ID
            payload = self._jwt_service.verify_token(token)
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check token type (should be access token)
            token_type = payload.get("type")
            if token_type != "access":  # nosec B105 - Standard JWT claim value, not a password
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Extract user ID from token
            user_id = self._jwt_service.extract_user_id(token)
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Get user from database
            user_repository = UserRepository(session)
            user = await user_repository.get_by_id(user_id)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is inactive",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    async def get_optional_current_user(
        self,
        credentials: HTTPAuthorizationCredentials | None,
        session: AsyncSession,
    ) -> User | None:
        """
        Get current authenticated user from JWT token (optional).

        This dependency allows for optional authentication - routes can handle
        both authenticated and unauthenticated requests.

        Args:
            credentials: Optional HTTP bearer token credentials
            session: Database session

        Returns:
            Current authenticated user if token is valid, None otherwise
        """
        if credentials is None:
            return None

        try:
            return await self.get_current_user(credentials, session)
        except HTTPException:
            return None


# Create global instance
auth_middleware = AuthenticationMiddleware()


# Export commonly used dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_database_session),
) -> User:
    """Dependency to get current authenticated user."""
    return await auth_middleware.get_current_user(credentials, session)


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security),
    session: AsyncSession = Depends(get_database_session),
) -> User | None:
    """Dependency to get optional current authenticated user."""
    return await auth_middleware.get_optional_current_user(credentials, session)


# Utility function to require specific permissions
def require_active_user(user: User = Depends(get_current_user)) -> User:
    """
    Dependency that requires an active authenticated user.

    Args:
        user: Current authenticated user

    Returns:
        The authenticated user

    Raises:
        HTTPException: If user is not active
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )

    return user


def require_verified_user(user: User = Depends(get_current_user)) -> User:
    """
    Dependency that requires a verified authenticated user.

    Args:
        user: Current authenticated user

    Returns:
        The authenticated user

    Raises:
        HTTPException: If user email is not verified
    """
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )

    return user
