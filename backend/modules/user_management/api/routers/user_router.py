"""
User API router for user management module.

This module contains FastAPI routes for user profile operations.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from modules.user_management.api.schemas.auth_schemas import ErrorResponse
from modules.user_management.api.schemas.user_schemas import (
    ChangePasswordRequest,
    UserDetailResponse,
    UserProfileUpdateRequest,
)
from modules.user_management.domain.entities.user import User
from modules.user_management.domain.exceptions import (
    UserManagementError,
    WeakPasswordError,
)
from modules.user_management.domain.ports.password_service_protocol import (
    PasswordServiceProtocol,
)
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)

router = APIRouter(prefix="/users", tags=["users"])


def create_user_router(
    user_repository: Callable[[], UserRepositoryProtocol],
    password_service: Callable[[], PasswordServiceProtocol],
    current_user_provider: Callable[[], User] | None = None,
) -> APIRouter:
    """Create user router with dependency injection."""

    # Use the provided current_user_provider or create a dummy one
    if current_user_provider:
        current_user_dep = Depends(current_user_provider)
    else:
        # Fallback - this will be replaced when the router is properly wired
        def dummy_current_user() -> User:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Current user provider not configured",
            )

        current_user_dep = Depends(dummy_current_user)

    @router.get(
        "/me",
        response_model=UserDetailResponse,
        responses={
            401: {"model": ErrorResponse, "description": "Unauthorized"},
        },
    )
    async def get_current_user_profile(  # pyright: ignore[reportUnusedFunction]
        current_user: Annotated[User, current_user_dep],
    ) -> UserDetailResponse:
        """Get current user profile."""
        return UserDetailResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            is_active=current_user.is_active,
            is_email_verified=current_user.is_email_verified,
            status=current_user.status.value,
            ml_user_id=current_user.ml_user_id,
            is_ml_connected=current_user.is_ml_connected,
            default_ml_site=current_user.default_ml_site,
            auto_publish=current_user.auto_publish,
            ai_confidence_threshold=current_user.ai_confidence_threshold,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            last_login_at=current_user.last_login_at,
            email_verified_at=current_user.email_verified_at,
        )

    @router.put(
        "/me",
        response_model=UserDetailResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Validation error"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
        },
    )
    async def update_user_profile(  # pyright: ignore[reportUnusedFunction]
        request: UserProfileUpdateRequest,
        current_user: Annotated[User, current_user_dep],
        user_repo: Annotated[UserRepositoryProtocol, Depends(user_repository)],
    ) -> UserDetailResponse:
        """Update current user profile."""
        try:
            current_user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                auto_publish=request.auto_publish,
                ai_confidence_threshold=request.ai_confidence_threshold,
                default_ml_site=request.default_ml_site,
            )

            updated_user = await user_repo.update(current_user)

            return UserDetailResponse(
                id=updated_user.id,
                email=updated_user.email,
                first_name=updated_user.first_name,
                last_name=updated_user.last_name,
                is_active=updated_user.is_active,
                is_email_verified=updated_user.is_email_verified,
                status=updated_user.status.value,
                ml_user_id=updated_user.ml_user_id,
                is_ml_connected=updated_user.is_ml_connected,
                default_ml_site=updated_user.default_ml_site,
                auto_publish=updated_user.auto_publish,
                ai_confidence_threshold=updated_user.ai_confidence_threshold,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at,
                last_login_at=updated_user.last_login_at,
                email_verified_at=updated_user.email_verified_at,
            )

        except UserManagementError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": e.error_code, "message": e.message},
            ) from e

    @router.post(
        "/me/change-password",
        responses={
            200: {"description": "Password changed successfully"},
            400: {"model": ErrorResponse, "description": "Validation error"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
        },
    )
    async def change_password(  # pyright: ignore[reportUnusedFunction]
        request: ChangePasswordRequest,
        current_user: Annotated[User, current_user_dep],
        user_repo: Annotated[UserRepositoryProtocol, Depends(user_repository)],
        password_svc: Annotated[PasswordServiceProtocol, Depends(password_service)],
    ) -> dict[str, str]:
        """Change current user password."""
        try:
            # Verify current password
            password_valid = await password_svc.verify_password(
                request.current_password, current_user.password_hash
            )

            if not password_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": "INVALID_CURRENT_PASSWORD",
                        "message": "Current password is incorrect",
                    },
                )

            # Validate new password strength
            from modules.user_management.domain.services.authentication import (
                AuthenticationService,
            )

            auth_service = AuthenticationService(
                user_repository=user_repo,
                password_service=password_svc,
            )

            if not auth_service._is_password_strong(request.new_password):  # pyright: ignore[reportPrivateUsage]
                raise WeakPasswordError()

            # Hash new password
            new_password_hash = await password_svc.hash_password(request.new_password)
            current_user.password_hash = new_password_hash

            await user_repo.update(current_user)

            return {"message": "Password changed successfully"}

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

    return router
