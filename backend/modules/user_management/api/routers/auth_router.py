"""
Authentication API router for user management module.

This module contains FastAPI routes for authentication endpoints.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.logging import get_structured_logger, set_user_id
from infrastructure.database import get_database_session
from modules.user_management.api.schemas.auth_schemas import (
    AuthErrorResponse,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    create_token_response,
    user_entity_to_response,
)
from modules.user_management.application.use_cases.authenticate_user import (
    AuthenticateUserUseCase,
)
from modules.user_management.application.use_cases.generate_tokens import (
    GenerateTokensUseCase,
)
from modules.user_management.application.use_cases.logout_user import LogoutUserUseCase
from modules.user_management.application.use_cases.refresh_token import (
    RefreshTokenUseCase,
)
from modules.user_management.application.use_cases.register_user import (
    RegisterUserUseCase,
)
from modules.user_management.domain.exceptions import (
    AccountInactiveError,
    AccountLockedError,
    UserAlreadyExistsError,
    WeakPasswordError,
)
from modules.user_management.domain.services.authentication import AuthenticationService
from modules.user_management.infrastructure.middleware.auth_middleware import (
    get_current_user,
)
from modules.user_management.infrastructure.middleware.simple_rate_limiter import (
    rate_limit_auth,
)
from modules.user_management.infrastructure.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from modules.user_management.infrastructure.repositories.user_repository import (
    UserRepository,
)
from modules.user_management.infrastructure.services.jwt_service import JWTService
from modules.user_management.infrastructure.services.password_service import (
    PasswordService,
)

# Create router with prefix and tags
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme for bearer token
security = HTTPBearer()

# Initialize structured logger
logger = get_structured_logger("auth_router")


# Dependency injection helpers
async def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> UserRepository:
    """Get user repository dependency."""
    return UserRepository(session)


async def get_refresh_token_repository(
    session: AsyncSession = Depends(get_database_session),
) -> RefreshTokenRepository:
    """Get refresh token repository dependency."""
    return RefreshTokenRepository(session)


async def get_password_service() -> PasswordService:
    """Get password service dependency."""
    return PasswordService()


async def get_jwt_service() -> JWTService:
    """Get JWT service dependency."""
    return JWTService()


async def get_authentication_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_service: PasswordService = Depends(get_password_service),
) -> AuthenticationService:
    """Get authentication service dependency."""
    return AuthenticationService(user_repository, password_service)


async def get_generate_tokens_use_case(
    jwt_service: JWTService = Depends(get_jwt_service),
    refresh_token_repository: RefreshTokenRepository = Depends(
        get_refresh_token_repository
    ),
) -> GenerateTokensUseCase:
    """Get generate tokens use case dependency."""
    return GenerateTokensUseCase(jwt_service, refresh_token_repository)


async def get_register_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),
    generate_tokens: GenerateTokensUseCase = Depends(get_generate_tokens_use_case),
) -> RegisterUserUseCase:
    """Get register user use case dependency."""
    return RegisterUserUseCase(auth_service, generate_tokens)


async def get_authenticate_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),
    generate_tokens: GenerateTokensUseCase = Depends(get_generate_tokens_use_case),
) -> AuthenticateUserUseCase:
    """Get authenticate user use case dependency."""
    return AuthenticateUserUseCase(auth_service, generate_tokens)


async def get_refresh_token_use_case(
    jwt_service: JWTService = Depends(get_jwt_service),
    refresh_token_repository: RefreshTokenRepository = Depends(
        get_refresh_token_repository
    ),
    user_repository: UserRepository = Depends(get_user_repository),
) -> RefreshTokenUseCase:
    """Get refresh token use case dependency."""
    return RefreshTokenUseCase(jwt_service, refresh_token_repository, user_repository)


async def get_logout_use_case(
    jwt_service: JWTService = Depends(get_jwt_service),
    refresh_token_repository: RefreshTokenRepository = Depends(
        get_refresh_token_repository
    ),
) -> LogoutUserUseCase:
    """Get logout user use case dependency."""
    return LogoutUserUseCase(jwt_service, refresh_token_repository)


# Authentication endpoints
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account and return JWT tokens for immediate login",
    responses={
        201: {"description": "User registered successfully", "model": TokenResponse},
        400: {"description": "Registration failed", "model": AuthErrorResponse},
        409: {"description": "User already exists", "model": AuthErrorResponse},
        429: {"description": "Too many requests", "model": AuthErrorResponse},
    },
)
@rate_limit_auth
async def register(
    request: RegisterRequest,
    http_request: Request,  # noqa: ARG001 - Used by rate_limit_auth decorator
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
) -> TokenResponse:
    """Register a new user account."""
    start_time = time.time()
    registration_id = f"register_{int(start_time * 1000)}"

    # Log registration attempt start
    logger.info(
        "Registration attempt started",
        email=request.email,
        registration_id=registration_id,
        has_first_name=request.first_name is not None,
        has_last_name=request.last_name is not None,
        timestamp=start_time,
    )

    try:
        result = await use_case.execute(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Set user context for subsequent logging
        set_user_id(str(result.user.id))

        # Log successful registration
        logger.security_event(
            "user_registered",
            severity="low",
            email=request.email,
            user_id=str(result.user.id),
            registration_id=registration_id,
            duration_ms=round(duration_ms, 2),
            auto_login=True,
        )

        # Log performance metrics
        logger.performance(
            "user_registration",
            duration_ms=duration_ms,
            success=True,
            registration_id=registration_id,
        )

        return create_token_response(result.user, result.tokens)

    except UserAlreadyExistsError:
        duration_ms = (time.time() - start_time) * 1000

        # Log duplicate registration attempt
        logger.security_event(
            "duplicate_registration",
            severity="medium",
            email=request.email,
            registration_id=registration_id,
            duration_ms=round(duration_ms, 2),
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from None
    except WeakPasswordError:
        duration_ms = (time.time() - start_time) * 1000

        # Log weak password attempt
        logger.security_event(
            "weak_password_attempt",
            severity="medium",
            email=request.email,
            registration_id=registration_id,
            duration_ms=round(duration_ms, 2),
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements",
        ) from None
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        # Log unexpected error
        logger.error(
            "Registration failed with unexpected error",
            email=request.email,
            registration_id=registration_id,
            duration_ms=round(duration_ms, 2),
            error=str(e),
            error_type=type(e).__name__,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user credentials and return JWT tokens",
    responses={
        200: {"description": "Login successful", "model": TokenResponse},
        401: {"description": "Invalid credentials", "model": AuthErrorResponse},
        423: {"description": "Account locked", "model": AuthErrorResponse},
        429: {"description": "Too many requests", "model": AuthErrorResponse},
    },
)
@rate_limit_auth
async def login(
    request: LoginRequest,
    http_request: Request,  # noqa: ARG001 - Used by rate_limit_auth decorator
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_use_case),
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    start_time = time.time()
    login_attempt_id = f"login_{int(start_time * 1000)}"

    # Log login attempt start
    logger.info(
        "Login attempt started",
        email=request.email,
        login_attempt_id=login_attempt_id,
        timestamp=start_time,
    )

    try:
        # Execute authentication use case
        result = await use_case.execute(request.email, request.password)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        if result is None:
            # Log failed login attempt
            logger.security_event(
                "login_failed",
                severity="medium",
                email=request.email,
                login_attempt_id=login_attempt_id,
                duration_ms=round(duration_ms, 2),
                failure_reason="invalid_credentials",
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Set user context for subsequent logging
        set_user_id(str(result.user.id))

        # Log successful login
        logger.security_event(
            "login_successful",
            severity="low",
            email=request.email,
            user_id=str(result.user.id),
            login_attempt_id=login_attempt_id,
            duration_ms=round(duration_ms, 2),
            last_login_at=result.user.last_login_at.isoformat()
            if result.user.last_login_at
            else None,
        )

        # Log performance metrics
        logger.performance(
            "user_login",
            duration_ms=duration_ms,
            success=True,
            login_attempt_id=login_attempt_id,
        )

        return create_token_response(result.user, result.tokens)

    except AccountLockedError as e:
        duration_ms = (time.time() - start_time) * 1000

        # Log account locked event
        logger.security_event(
            "account_locked",
            severity="high",
            email=request.email,
            login_attempt_id=login_attempt_id,
            duration_ms=round(duration_ms, 2),
            failed_attempts=e.failed_attempts,
            max_attempts=e.max_attempts,
        )

        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked after {e.failed_attempts} failed attempts",
        ) from e
    except AccountInactiveError:
        duration_ms = (time.time() - start_time) * 1000

        # Log inactive account access attempt
        logger.security_event(
            "inactive_account_access",
            severity="medium",
            email=request.email,
            login_attempt_id=login_attempt_id,
            duration_ms=round(duration_ms, 2),
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        ) from None
    except HTTPException:
        # Re-raise HTTPExceptions (like 401 Unauthorized) without converting to 500
        raise
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        # Log unexpected error
        logger.error(
            "Login failed with unexpected error",
            email=request.email,
            login_attempt_id=login_attempt_id,
            duration_ms=round(duration_ms, 2),
            error=str(e),
            error_type=type(e).__name__,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        ) from e


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Generate new access token using refresh token",
    responses={
        200: {"description": "Token refreshed successfully", "model": TokenResponse},
        401: {"description": "Invalid refresh token", "model": AuthErrorResponse},
    },
)
async def refresh_token(
    request: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        result = await use_case.execute(request.refresh_token)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        return create_token_response(result.user, result.tokens)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        ) from e


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout user and invalidate refresh tokens",
    responses={
        200: {"description": "Logout successful", "model": LogoutResponse},
        401: {"description": "Invalid token", "model": AuthErrorResponse},
    },
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    use_case: LogoutUserUseCase = Depends(get_logout_use_case),
) -> LogoutResponse:
    """Logout user and invalidate tokens."""
    try:
        access_token = credentials.credentials
        success = await use_case.execute(access_token=access_token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return LogoutResponse(message="Logged out successfully")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        ) from e


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get current user profile information",
    responses={
        200: {"description": "User profile retrieved", "model": UserResponse},
        401: {"description": "Invalid token", "model": AuthErrorResponse},
    },
)
async def get_me(
    current_user=Depends(get_current_user),
) -> UserResponse:
    """Get current user profile."""
    return user_entity_to_response(current_user)
