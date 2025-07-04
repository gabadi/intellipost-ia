"""
Authentication API router using the correct protocol architecture.

This router only knows about API-owned protocols and schemas.
It does NOT import anything from modules.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.container import AuthenticationProviderDep
from api.protocols.authentication_provider import (
    AuthenticationCredentials,
    UserRegistrationData,
)
from api.schemas.auth_schemas import (
    AuthErrorResponse,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from infrastructure.config.logging import get_structured_logger

# Create router with prefix and tags
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme for bearer token
security = HTTPBearer()

# Initialize structured logger
logger = get_structured_logger("auth_router")


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
    },
)
async def register(
    request: RegisterRequest,
    auth_provider: AuthenticationProviderDep,
) -> TokenResponse:
    """Register a new user account."""
    try:
        # Convert API request to protocol request
        registration_data = UserRegistrationData(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        # Use the authentication provider protocol
        result = await auth_provider.register_user(registration_data)

        # Convert protocol result to API response
        return TokenResponse(
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
            token_type=result.tokens.token_type,
            user=UserResponse(
                id=result.user.id,
                email=result.user.email,
                first_name=result.user.first_name,
                last_name=result.user.last_name,
                is_active=result.user.is_active,
                created_at=result.user.created_at,
                last_login_at=result.user.last_login_at,
            ),
        )

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    },
)
async def login(
    request: LoginRequest,
    auth_provider: AuthenticationProviderDep,
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    try:
        # Convert API request to protocol request
        credentials = AuthenticationCredentials(
            email=request.email,
            password=request.password,
        )

        # Use the authentication provider protocol
        result = await auth_provider.authenticate_user(credentials)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Convert protocol result to API response
        return TokenResponse(
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
            token_type=result.tokens.token_type,
            user=UserResponse(
                id=result.user.id,
                email=result.user.email,
                first_name=result.user.first_name,
                last_name=result.user.last_name,
                is_active=result.user.is_active,
                created_at=result.user.created_at,
                last_login_at=result.user.last_login_at,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
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
    auth_provider: AuthenticationProviderDep,
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        result = await auth_provider.refresh_tokens(request.refresh_token)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        return TokenResponse(
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
            token_type=result.tokens.token_type,
            user=UserResponse(
                id=result.user.id,
                email=result.user.email,
                first_name=result.user.first_name,
                last_name=result.user.last_name,
                is_active=result.user.is_active,
                created_at=result.user.created_at,
                last_login_at=result.user.last_login_at,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
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
    auth_provider: AuthenticationProviderDep,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> LogoutResponse:
    """Logout user and invalidate tokens."""
    try:
        access_token = credentials.credentials
        success = await auth_provider.logout_user(access_token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return LogoutResponse(message="Logged out successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
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
    auth_provider: AuthenticationProviderDep,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserResponse:
    """Get current user profile."""
    try:
        access_token = credentials.credentials
        user = await auth_provider.get_current_user(access_token)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile",
        ) from e
