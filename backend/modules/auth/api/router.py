"""
Authentication API router.

This module contains FastAPI routes for authentication operations.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.settings import settings
from infrastructure.database import get_database_session
from modules.auth.application.authentication_service import AuthenticationServiceImpl
from modules.auth.domain.models import AuthenticatedUser

from .schemas import (
    AuthResponse,
    ChangePasswordRequest,
    ErrorResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SessionResponse,
    TokenResponse,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_database_session)],
) -> AuthenticationServiceImpl:
    """Dependency to get authentication service."""
    return AuthenticationServiceImpl(db)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
) -> AuthenticatedUser:
    """Dependency to get current authenticated user."""
    try:
        return await auth_service.validate_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        409: {"model": ErrorResponse, "description": "Registration failed"},
    },
)
async def register(
    request: RegisterRequest,
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    response: Response,
) -> AuthResponse:
    """
    Register a new user.

    Creates a new user account and returns authentication tokens.
    """
    try:
        result = await auth_service.register_user(request.email, request.password)

        # Set secure cookies for web clients
        if settings.is_production:
            response.set_cookie(
                key="access_token",
                value=result.access_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=settings.jwt_access_token_expire_minutes * 60,
            )
            response.set_cookie(
                key="refresh_token",
                value=result.refresh_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
            )

        return AuthResponse(
            user_id=result.user_id,
            email=result.email,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
        )
    except ValueError as e:
        if "already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Registration failed"
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid registration data"
        ) from e


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        423: {"model": ErrorResponse, "description": "Account locked"},
    },
)
async def login(
    request: LoginRequest,
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    response: Response,
) -> AuthResponse:
    """
    Login with email and password.

    Authenticates user credentials and returns authentication tokens.
    """
    try:
        result = await auth_service.authenticate_user(request.email, request.password)

        # Set secure cookies for web clients
        if settings.is_production:
            response.set_cookie(
                key="access_token",
                value=result.access_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=settings.jwt_access_token_expire_minutes * 60,
            )
            response.set_cookie(
                key="refresh_token",
                value=result.refresh_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
            )

        return AuthResponse(
            user_id=result.user_id,
            email=result.email,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
        )
    except ValueError as e:
        if "locked" in str(e):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED, detail="Account temporarily locked"
            ) from e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        ) from e


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def logout(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    response: Response,
) -> None:
    """
    Logout current user.

    Invalidates all refresh tokens for the user.
    """
    await auth_service.logout_user(current_user.user_id)

    # Clear cookies for web clients
    if settings.is_production:
        response.delete_cookie(key="access_token", secure=True, httponly=True)
        response.delete_cookie(key="refresh_token", secure=True, httponly=True)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse, "description": "Invalid refresh token"}},
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
    response: Response,
    refresh_token_cookie: Annotated[str | None, Cookie()] = None,
) -> TokenResponse:
    """
    Refresh authentication tokens.

    Uses a valid refresh token to obtain new access and refresh tokens.
    """
    # Use token from request body or cookie
    token = request.refresh_token or refresh_token_cookie
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required"
        )

    try:
        result = await auth_service.refresh_token(token)

        # Update cookies for web clients
        if settings.is_production:
            response.set_cookie(
                key="access_token",
                value=result.access_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=settings.jwt_access_token_expire_minutes * 60,
            )
            response.set_cookie(
                key="refresh_token",
                value=result.refresh_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
            )

        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


@router.get(
    "/session",
    response_model=SessionResponse,
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def get_session(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> SessionResponse:
    """
    Get current session information.

    Returns information about the current authenticated session.
    """
    return SessionResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        created_at=datetime.utcnow().isoformat(),
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid password"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    auth_service: Annotated[AuthenticationServiceImpl, Depends(get_auth_service)],
) -> None:
    """
    Change user password.

    Changes the current user's password and invalidates all existing sessions.
    """
    try:
        await auth_service.change_password(
            current_user.user_id, request.current_password, request.new_password
        )
    except ValueError as e:
        # Use generic error message for security
        if "incorrect" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password change failed",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password requirements",
        ) from e
