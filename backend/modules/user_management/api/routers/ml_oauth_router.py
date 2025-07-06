"""
MercadoLibre OAuth API router for user management module.

This module contains the FastAPI router for ML OAuth endpoints
with authentication, validation, and error handling.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_database_session
from api.dependencies import get_current_user
from modules.user_management.api.schemas.ml_oauth_schemas import (
    MLConnectionStatusResponse,
    MLDisconnectRequest,
    MLDisconnectResponse,
    MLErrorResponse,
    MLManagerAccountError,
    MLOAuthCallbackRequest,
    MLOAuthCallbackResponse,
    MLOAuthInitiateRequest,
    MLOAuthInitiateResponse,
    MLRateLimitResponse,
    MLTokenRefreshResponse,
)
from modules.user_management.application.use_cases.disconnect_ml import (
    DisconnectMLUseCase,
)
from modules.user_management.application.use_cases.get_ml_connection_status import (
    GetMLConnectionStatusUseCase,
)
from modules.user_management.application.use_cases.handle_ml_callback import (
    HandleMLCallbackUseCase,
)
from modules.user_management.application.use_cases.initiate_ml_oauth import (
    InitiateMLOAuthUseCase,
)
from modules.user_management.application.use_cases.refresh_ml_token import (
    RefreshMLTokenUseCase,
)
from modules.user_management.domain.entities.user import User
from modules.user_management.domain.exceptions import (
    AuthenticationError,
    ValidationError,
)
from modules.user_management.domain.services.ml_oauth import MLOAuthService
from modules.user_management.infrastructure.models.ml_credentials_model import (
    MLCredentialsModel,
)
from modules.user_management.infrastructure.repositories.sqlalchemy_ml_credentials_repository import (
    SQLAlchemyMLCredentialsRepository,
)
from modules.user_management.infrastructure.services.credential_encryption_service import (
    CredentialEncryptionService,
)
from modules.user_management.infrastructure.services.mercadolibre_api_client import (
    MercadoLibreAPIClient,
    MLManagerAccountError as MLManagerAccountAPIError,
    MLRateLimitError,
)

# Configure logging
logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(
    prefix="/auth/ml",
    tags=["MercadoLibre OAuth"],
    responses={
        401: {"model": MLErrorResponse, "description": "Unauthorized"},
        403: {"model": MLManagerAccountError, "description": "Manager account required"},
        429: {"model": MLRateLimitResponse, "description": "Rate limit exceeded"},
        500: {"model": MLErrorResponse, "description": "Internal server error"},
    },
)

# Security
bearer_scheme = HTTPBearer()


async def get_current_user_id_from_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> str:
    """Extract user ID from authenticated user."""
    return str(current_user.id)


async def get_oauth_service(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> MLOAuthService:
    """Create ML OAuth service with dependencies."""
    # Get configuration from settings
    from infrastructure.config.settings import settings
    
    app_id = settings.ml_app_id or "test_app_id"
    app_secret = settings.ml_app_secret or "test_app_secret"
    
    # Create dependencies
    ml_client = MercadoLibreAPIClient(app_id, app_secret)
    credentials_repository = SQLAlchemyMLCredentialsRepository(db_session)
    encryption_service = CredentialEncryptionService()
    
    # Create service
    return MLOAuthService(
        ml_client=ml_client,
        credentials_repository=credentials_repository,
        encryption_service=encryption_service,
        app_id=app_id,
        app_secret=app_secret,
    )


@router.post(
    "/initiate",
    response_model=MLOAuthInitiateResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate MercadoLibre OAuth flow",
    description="Start OAuth 2.0 flow with PKCE for MercadoLibre integration",
)
async def initiate_oauth(
    request: MLOAuthInitiateRequest,
    user_id: Annotated[str, Depends(get_current_user_id_from_user)],
    oauth_service: Annotated[MLOAuthService, Depends(get_oauth_service)],
) -> MLOAuthInitiateResponse:
    """Initiate MercadoLibre OAuth flow."""
    try:
        # Create use case
        use_case = InitiateMLOAuthUseCase(oauth_service)
        
        # Execute OAuth initiation
        flow_data = await use_case.execute(
            user_id=user_id,
            redirect_uri=request.redirect_uri,
            site_id=request.site_id,
        )
        
        logger.info(f"OAuth flow initiated for user {user_id}, site {request.site_id}")
        
        return MLOAuthInitiateResponse(
            authorization_url=flow_data.authorization_url,
            state=flow_data.state,
            code_verifier=flow_data.code_verifier,
        )
        
    except ValidationError as e:
        logger.warning(f"OAuth initiation validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "error_description": str(e)},
        )
    except Exception as e:
        logger.error(f"OAuth initiation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "error_description": "Failed to initiate OAuth flow"},
        )


@router.post(
    "/callback",
    response_model=MLOAuthCallbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Handle MercadoLibre OAuth callback",
    description="Complete OAuth flow by exchanging code for tokens with manager account validation",
)
async def handle_callback(
    request: MLOAuthCallbackRequest,
    user_id: Annotated[str, Depends(get_current_user_id_from_user)],
    oauth_service: Annotated[MLOAuthService, Depends(get_oauth_service)],
) -> MLOAuthCallbackResponse:
    """Handle MercadoLibre OAuth callback."""
    try:
        # Create use case
        use_case = HandleMLCallbackUseCase(oauth_service)
        
        # Execute callback handling
        credentials = await use_case.execute(
            user_id=user_id,
            code=request.code,
            state=request.state,
            code_verifier=request.code_verifier,
        )
        
        logger.info(f"OAuth callback completed for user {user_id}")
        
        return MLOAuthCallbackResponse(
            success=True,
            message="MercadoLibre account connected successfully",
            ml_nickname=credentials.ml_nickname,
            ml_email=credentials.ml_email,
            ml_site_id=credentials.ml_site_id,
            connection_health=credentials.connection_health,
        )
        
    except MLManagerAccountAPIError as e:
        logger.warning(f"Manager account validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "manager_account_required",
                "error_description": "Only manager accounts can authorize applications. "
                                   "Collaborator accounts cannot connect to IntelliPost AI.",
                "guidance": "Please use a MercadoLibre manager account to complete the connection.",
            },
        )
    except ValidationError as e:
        logger.warning(f"OAuth callback validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "error_description": str(e)},
        )
    except AuthenticationError as e:
        logger.warning(f"OAuth callback authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "authentication_failed", "error_description": str(e)},
        )
    except MLRateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limited",
                "error_description": "Too many requests. Please try again later.",
                "retry_after": e.retry_after or 60,
            },
        )
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "error_description": "Failed to complete OAuth flow"},
        )


@router.get(
    "/status",
    response_model=MLConnectionStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get MercadoLibre connection status",
    description="Check current connection status and health",
)
async def get_connection_status(
    user_id: Annotated[str, Depends(get_current_user_id_from_user)],
    oauth_service: Annotated[MLOAuthService, Depends(get_oauth_service)],
) -> MLConnectionStatusResponse:
    """Get MercadoLibre connection status."""
    try:
        # Create use case
        use_case = GetMLConnectionStatusUseCase(oauth_service)
        
        # Execute status check
        status_info = await use_case.execute(user_id)
        
        # Get credentials for additional info
        credentials = await oauth_service.get_user_credentials(user_id)
        
        return MLConnectionStatusResponse(
            is_connected=status_info.is_connected,
            connection_health=status_info.connection_health,
            ml_nickname=status_info.ml_nickname,
            ml_email=status_info.ml_email,
            ml_site_id=status_info.ml_site_id,
            expires_at=status_info.expires_at,
            last_validated_at=status_info.last_validated_at,
            error_message=status_info.error_message,
            should_refresh=credentials.should_refresh_token if credentials else False,
            time_until_refresh=credentials.time_until_refresh() if credentials else None,
        )
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "error_description": "Failed to check connection status"},
        )


@router.post(
    "/disconnect",
    response_model=MLDisconnectResponse,
    status_code=status.HTTP_200_OK,
    summary="Disconnect MercadoLibre account",
    description="Remove MercadoLibre integration and credentials",
)
async def disconnect(
    request: MLDisconnectRequest,
    user_id: Annotated[str, Depends(get_current_user_id_from_user)],
    oauth_service: Annotated[MLOAuthService, Depends(get_oauth_service)],
) -> MLDisconnectResponse:
    """Disconnect MercadoLibre account."""
    try:
        # Create use case
        use_case = DisconnectMLUseCase(oauth_service)
        
        # Execute disconnection
        success = await use_case.execute(user_id)
        
        if success:
            logger.info(f"MercadoLibre disconnected for user {user_id}")
            return MLDisconnectResponse(
                success=True,
                message="MercadoLibre account disconnected successfully",
            )
        else:
            return MLDisconnectResponse(
                success=False,
                message="No MercadoLibre connection found",
            )
        
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "error_description": "Failed to disconnect account"},
        )


@router.post(
    "/refresh",
    response_model=MLTokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh MercadoLibre tokens",
    description="Manually refresh access tokens (normally done automatically)",
)
async def refresh_tokens(
    user_id: Annotated[str, Depends(get_current_user_id_from_user)],
    oauth_service: Annotated[MLOAuthService, Depends(get_oauth_service)],
) -> MLTokenRefreshResponse:
    """Refresh MercadoLibre tokens."""
    try:
        # Create use case
        use_case = RefreshMLTokenUseCase(oauth_service)
        
        # Execute token refresh
        credentials = await use_case.execute(user_id)
        
        logger.info(f"Tokens refreshed for user {user_id}")
        
        return MLTokenRefreshResponse(
            success=True,
            message="Tokens refreshed successfully",
            expires_at=credentials.ml_expires_at,
            connection_health=credentials.connection_health,
        )
        
    except AuthenticationError as e:
        logger.warning(f"Token refresh authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "refresh_failed", "error_description": str(e)},
        )
    except MLRateLimitError as e:
        logger.warning(f"Rate limit exceeded during refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limited",
                "error_description": "Too many requests. Please try again later.",
                "retry_after": e.retry_after or 60,
            },
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "error_description": "Failed to refresh tokens"},
        )