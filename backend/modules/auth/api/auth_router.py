"""
Authentication API router.

This module contains FastAPI router for authentication endpoints including
registration, login, logout, token refresh, and user profile retrieval.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from di.auth_container import get_auth_service
from infrastructure.config.settings import Settings
from modules.auth.api.schemas import (
    AccessTokenResponse,
    AuthenticationResponse,
    ErrorResponse,
    LogoutRequest,
    MessageResponse,
    PasswordChangeRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegistrationRequest,
    UserResponse,
    user_to_response,
)
from modules.auth.domain.protocols import AuthenticationServiceProtocol

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
    async def register_user(  # pyright: ignore[reportUnusedFunction]
        user_data: UserRegistrationRequest,
        auth_service: Annotated[
            AuthenticationServiceProtocol, Depends(get_auth_service)
        ],
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
    async def login_user(  # pyright: ignore[reportUnusedFunction]
        credentials: UserLoginRequest,
        auth_service: Annotated[
            AuthenticationServiceProtocol, Depends(get_auth_service)
        ],
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
    async def refresh_access_token(  # pyright: ignore[reportUnusedFunction]
        request: TokenRefreshRequest,
        auth_service: Annotated[
            AuthenticationServiceProtocol, Depends(get_auth_service)
        ],
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
    async def logout_user(  # pyright: ignore[reportUnusedFunction]
        request: LogoutRequest,
        auth_service: Annotated[
            AuthenticationServiceProtocol, Depends(get_auth_service)
        ],
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
    async def get_current_user_profile(  # pyright: ignore[reportUnusedFunction]
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        auth_service: Annotated[
            AuthenticationServiceProtocol, Depends(get_auth_service)
        ],
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
            # Get user profile using auth service
            user = await auth_service.get_user_profile(credentials.credentials)
            return user_to_response(user)

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    @router.post(
        "/change-password",
        response_model=MessageResponse,
        summary="Change user password",
        description="Change authenticated user's password after verifying current password",
        responses={
            200: {"description": "Password changed successfully"},
            400: {
                "model": ErrorResponse,
                "description": "Invalid password or validation error",
            },
            401: {
                "model": ErrorResponse,
                "description": "Authentication required or current password incorrect",
            },
        },
    )
    async def change_password(  # pyright: ignore[reportUnusedFunction]
        request: PasswordChangeRequest,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        auth_service: Annotated[
            AuthenticationServiceProtocol, Depends(get_auth_service)
        ],
    ) -> MessageResponse:
        """
        Change user password.

        Validates the current password and updates to the new password
        if validation passes.
        """
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Change password using auth service
            success = await auth_service.change_password(
                access_token=credentials.credentials,
                current_password=request.current_password,
                new_password=request.new_password,
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to change password",
                )

            return MessageResponse(message="Password changed successfully")

        except ValueError as e:
            # Handle validation errors and incorrect current password
            error_message = str(e)
            if "current password is incorrect" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_message,
                ) from e
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                ) from e
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    return router


# Create default router instance
default_router = create_auth_router(Settings())
