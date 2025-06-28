"""
Authentication API router.

This module contains FastAPI router for authentication endpoints including
registration, login, logout, token refresh, and user profile retrieval.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.settings import Settings
from infrastructure.database import get_database_session
from modules.auth.api.schemas import (
    AccessTokenResponse,
    AuthenticationResponse,
    ErrorResponse,
    LogoutRequest,
    MessageResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegistrationRequest,
    UserResponse,
    user_to_response,
)
from modules.auth.application.authentication_service_impl import (
    AuthenticationServiceImpl,
)
from modules.auth.infrastructure.jwt_service import JWTService
from modules.auth.infrastructure.middleware import create_auth_dependencies
from modules.auth.infrastructure.password_service import PasswordService
from modules.user.infrastructure.user_repository import UserRepository

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer(auto_error=False)


def create_auth_router(settings: Settings) -> APIRouter:
    """
    Create authentication router with dependency injection.

    Args:
        settings: Application settings

    Returns:
        APIRouter: Configured authentication router
    """

    # Create services
    password_service = PasswordService()
    jwt_service = JWTService(settings)

    def get_auth_service(
        db_session: Annotated[AsyncSession, Depends(get_database_session)],
    ) -> AuthenticationServiceImpl:
        """Create authentication service with database session."""
        user_repository = UserRepository(db_session)
        return AuthenticationServiceImpl(user_repository, password_service, jwt_service)

    # Create a dummy auth service for dependency setup (will be overridden by get_auth_service)
    from uuid import UUID

    from modules.user.domain.user import User

    # We need to create dependencies without a real repository
    # The actual repository will be injected at request time via get_auth_service
    class DummyUserRepository:
        """Dummy repository for type checking only."""

        async def create(self, user: User) -> User:
            raise NotImplementedError("This is a dummy repository")

        async def get_by_id(self, user_id: UUID) -> User | None:
            raise NotImplementedError("This is a dummy repository")

        async def get_by_email(self, email: str) -> User | None:
            raise NotImplementedError("This is a dummy repository")

        async def update(self, user: User) -> User:
            raise NotImplementedError("This is a dummy repository")

        async def delete(self, user_id: UUID) -> bool:
            raise NotImplementedError("This is a dummy repository")

        async def email_exists(self, email: str) -> bool:
            raise NotImplementedError("This is a dummy repository")

        async def update_last_login(self, user_id: UUID) -> None:
            raise NotImplementedError("This is a dummy repository")

    dummy_auth_service = AuthenticationServiceImpl(
        DummyUserRepository(), password_service, jwt_service
    )

    get_current_user, get_current_active_user, get_optional_current_user = (
        create_auth_dependencies(dummy_auth_service)
    )

    @router.post(
        "/register",
        response_model=AuthenticationResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Register new user account",
        description="Create a new user account with email and password validation",
        responses={
            201: {"description": "User registered successfully"},
            400: {"model": ErrorResponse, "description": "Invalid registration data"},
            409: {"model": ErrorResponse, "description": "User already exists"},
        },
    )
    async def register_user(
        user_data: UserRegistrationRequest,
        auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    ) -> AuthenticationResponse:
        """
        Register a new user account.

        Creates a new user with email and password validation, returns user
        information and authentication tokens.
        """
        result = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

        if not result.success:
            error_message = result.error_message or "Unknown error"
            if "already exists" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )

        # Ensure we have all required data for successful response
        if (
            not result.user
            or not result.access_token
            or not result.refresh_token
            or result.expires_in is None
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration succeeded but missing required response data",
            )

        return AuthenticationResponse(
            user=user_to_response(result.user),
            tokens=TokenResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                token_type=result.token_type,
                expires_in=result.expires_in,
            ),
            message="Registration successful",
        )

    @router.post(
        "/login",
        response_model=AuthenticationResponse,
        summary="User login",
        description="Authenticate user with email and password, returns JWT tokens",
        responses={
            200: {"description": "Login successful"},
            401: {"model": ErrorResponse, "description": "Invalid credentials"},
            403: {"model": ErrorResponse, "description": "Account not active"},
        },
    )
    async def login_user(
        credentials: UserLoginRequest,
        auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    ) -> AuthenticationResponse:
        """
        Authenticate user with email and password.

        Validates credentials and returns user information with JWT tokens.
        """
        result = await auth_service.authenticate_user(
            email=credentials.email,
            password=credentials.password,
        )

        if not result.success:
            error_message = result.error_message or "Unknown error"
            if "not active" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_message,
                )

        # Ensure we have all required data for successful response
        if (
            not result.user
            or not result.access_token
            or not result.refresh_token
            or result.expires_in is None
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login succeeded but missing required response data",
            )

        return AuthenticationResponse(
            user=user_to_response(result.user),
            tokens=TokenResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                token_type=result.token_type,
                expires_in=result.expires_in,
            ),
            message="Login successful",
        )

    @router.post(
        "/refresh",
        response_model=AccessTokenResponse,
        summary="Refresh access token",
        description="Generate new access token using valid refresh token",
        responses={
            200: {"description": "Token refreshed successfully"},
            401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        },
    )
    async def refresh_access_token(
        request: TokenRefreshRequest,
        auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    ) -> AccessTokenResponse:
        """
        Refresh access token using refresh token.

        Generates a new access token from a valid refresh token.
        """
        try:
            new_access_token = await auth_service.refresh_token(request.refresh_token)

            return AccessTokenResponse(
                access_token=new_access_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60,
            )

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}",
            ) from e

    @router.post(
        "/logout",
        response_model=MessageResponse,
        summary="User logout",
        description="Logout user by validating refresh token",
        responses={
            200: {"description": "Logout successful"},
            401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        },
    )
    async def logout_user(
        request: LogoutRequest,
        auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    ) -> MessageResponse:
        """
        Logout user by validating refresh token.

        Note: In this MVP implementation, tokens are not blacklisted,
        but the refresh token is validated.
        """
        success = await auth_service.logout_user(request.refresh_token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return MessageResponse(message="Logout successful")

    @router.get(
        "/me",
        response_model=UserResponse,
        summary="Get current user profile",
        description="Get current authenticated user's profile information",
        responses={
            200: {"description": "User profile retrieved successfully"},
            401: {"model": ErrorResponse, "description": "Authentication required"},
        },
    )
    async def get_current_user_profile(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
        db_session: Annotated[AsyncSession, Depends(get_database_session)],
    ) -> UserResponse:
        """
        Get current authenticated user's profile.

        Returns detailed user information for the authenticated user.
        """
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Validate token and get user info
            auth_user = await auth_service.validate_token(credentials.credentials)

            # Get full user details from repository
            user_repository = UserRepository(db_session)
            user = await user_repository.get_by_id(auth_user.user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            return user_to_response(user)

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    return router


# Create default router instance
default_router = create_auth_router(Settings())
