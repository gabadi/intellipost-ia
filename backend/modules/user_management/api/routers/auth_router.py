"""
Authentication API router for user management module.

This module contains FastAPI routes for user authentication operations.
"""

from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from modules.user_management.api.schemas.auth_schemas import (
    ErrorResponse,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from modules.user_management.application.use_cases.authenticate_user import (
    AuthenticateUserUseCase,
)
from modules.user_management.application.use_cases.refresh_token import (
    RefreshTokenUseCase,
)
from modules.user_management.application.use_cases.register_user import (
    RegisterUserUseCase,
)
from modules.user_management.domain.exceptions import (
    AccountInactiveError,
    AccountLockedError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserManagementError,
    UserNotFoundError,
    WeakPasswordError,
)

# Import dependencies will be injected by FastAPI

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


def create_auth_router(
    register_use_case_factory: Callable[[], RegisterUserUseCase],
    authenticate_use_case_factory: Callable[[], AuthenticateUserUseCase],
    refresh_token_use_case_factory: Callable[[], RefreshTokenUseCase],
    access_token_expire_minutes: int = 15,
    registration_enabled: bool = False,
) -> APIRouter:
    """Create authentication router with dependency injection."""

    @router.post(
        "/register",
        response_model=TokenResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            400: {"model": ErrorResponse, "description": "Validation error"},
            409: {"model": ErrorResponse, "description": "User already exists"},
        },
    )
    async def register(  # pyright: ignore[reportUnusedFunction]
        request: RegisterRequest,
        register_use_case: RegisterUserUseCase = Depends(register_use_case_factory),
        authenticate_use_case: AuthenticateUserUseCase = Depends(
            authenticate_use_case_factory
        ),
    ) -> TokenResponse:
        """Register a new user account."""
        if not registration_enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "REGISTRATION_DISABLED",
                    "message": "User registration is currently disabled",
                },
            )

        try:
            user = await register_use_case.execute(
                email=request.email,
                password=request.password,
                first_name=request.first_name,
                last_name=request.last_name,
            )

            # Generate tokens for immediate login after registration
            access_token, refresh_token, _ = await authenticate_use_case.execute(
                request.email, request.password
            )

            user_response = UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_email_verified=user.is_email_verified,
                status=user.status.value,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=access_token_expire_minutes * 60,
                user=user_response,
            )

        except UserAlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e
        except WeakPasswordError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e
        except UserManagementError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e

    @router.post(
        "/login",
        response_model=TokenResponse,
        responses={
            401: {"model": ErrorResponse, "description": "Invalid credentials"},
            423: {"model": ErrorResponse, "description": "Account locked"},
        },
    )
    async def login(  # pyright: ignore[reportUnusedFunction]
        request: LoginRequest,
        authenticate_use_case: AuthenticateUserUseCase = Depends(
            authenticate_use_case_factory
        ),
    ) -> TokenResponse:
        """Authenticate user and return JWT tokens."""
        try:
            access_token, refresh_token, user = await authenticate_use_case.execute(
                request.email, request.password
            )

            user_response = UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_email_verified=user.is_email_verified,
                status=user.status.value,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=access_token_expire_minutes * 60,
                user=user_response,
            )

        except InvalidCredentialsError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e
        except AccountLockedError as e:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "error_code": e.error_code,
                    "message": e.message,
                    "details": {
                        "failed_attempts": e.failed_attempts,
                        "max_attempts": e.max_attempts,
                    },
                },
            ) from e
        except AccountInactiveError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e
        except UserManagementError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e

    @router.post(
        "/refresh",
        response_model=TokenResponse,
        responses={
            401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        },
    )
    async def refresh_token(  # pyright: ignore[reportUnusedFunction]
        request: RefreshTokenRequest,
        refresh_token_use_case: RefreshTokenUseCase = Depends(
            refresh_token_use_case_factory
        ),
    ) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            access_token, refresh_token, user = await refresh_token_use_case.execute(
                request.refresh_token
            )

            user_response = UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_email_verified=user.is_email_verified,
                status=user.status.value,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=access_token_expire_minutes * 60,
                user=user_response,
            )

        except (InvalidTokenError, UserNotFoundError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e
        except UserManagementError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e

    @router.post(
        "/logout",
        response_model=LogoutResponse,
        responses={
            401: {"model": ErrorResponse, "description": "Invalid token"},
        },
    )
    async def logout() -> LogoutResponse:  # pyright: ignore[reportUnusedFunction]
        """
        Logout user and invalidate tokens.

        Note: For stateless JWT, this is primarily for client-side token cleanup.
        In a production system, you might want to implement token blacklisting.
        """
        return LogoutResponse()

    return router
