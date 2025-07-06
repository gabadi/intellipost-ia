"""
FastAPI authentication middleware for JWT token validation.

This module provides middleware for protecting routes with JWT authentication.
"""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from modules.user_management.domain.entities.user import User
from modules.user_management.domain.ports.jwt_service_protocol import JWTServiceProtocol
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)

security = HTTPBearer()


class AuthMiddleware:
    """FastAPI authentication middleware."""

    def __init__(
        self,
        jwt_service: JWTServiceProtocol,
        user_repository: UserRepositoryProtocol,
    ):
        self.jwt_service = jwt_service
        self.user_repository = user_repository

    async def get_current_user(
        self, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ) -> User:
        """Get current authenticated user from JWT token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Verify token
            payload = self.jwt_service.verify_token(credentials.credentials)
            if payload is None:
                raise credentials_exception

            # Extract user ID
            user_id = self.jwt_service.extract_user_id(credentials.credentials)
            if user_id is None:
                raise credentials_exception

            # Check token type
            if payload.get("type") != "access":
                raise credentials_exception

        except Exception as e:
            raise credentials_exception from e

        # Get user from database
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise credentials_exception

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        return user

    def get_current_active_user(self) -> Callable[..., Awaitable[User]]:
        """Get dependency function for current active user."""

        async def _get_current_active_user(
            current_user: Annotated[User, Depends(self.get_current_user)],
        ) -> User:
            """Get current active user (additional check)."""
            if not current_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
                )
            return current_user

        return _get_current_active_user


def create_auth_dependency(
    jwt_service: JWTServiceProtocol, user_repository: UserRepositoryProtocol
):
    """Create FastAPI dependency for authentication."""
    auth_middleware = AuthMiddleware(jwt_service, user_repository)

    async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> User:
        return await auth_middleware.get_current_user(credentials)

    return get_current_user
