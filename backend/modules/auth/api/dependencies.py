"""
Authentication dependencies for FastAPI.

This module provides reusable authentication dependencies.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_database_session
from modules.auth.application.authentication_service import AuthenticationServiceImpl
from modules.auth.domain.models import AuthenticatedUser

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_database_session)],
) -> AuthenticationServiceImpl:
    """Get authentication service instance."""
    return AuthenticationServiceImpl(db)


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
) -> AuthenticatedUser | None:
    """
    Get current user if authenticated, otherwise return None.

    Use this for endpoints that support both authenticated and anonymous access.
    """
    if not credentials:
        return None

    try:
        return await auth_service.validate_token(credentials.credentials)
    except ValueError:
        return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
) -> AuthenticatedUser:
    """
    Get current authenticated user.

    Use this for endpoints that require authentication.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return await auth_service.validate_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
OptionalUser = Annotated[AuthenticatedUser | None, Depends(get_current_user_optional)]
