"""
User API router.

This module contains FastAPI routes for user operations.
"""

from fastapi import APIRouter

from modules.auth.api.dependencies import CurrentUser
from modules.user.api.schemas import UserProfileResponse, UserProfileUpdateRequest

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    responses={401: {"description": "Not authenticated"}},
)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> UserProfileResponse:
    """
    Get current user profile.

    Requires authentication via Bearer token.
    """
    # TODO: Implement user profile service
    return UserProfileResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        first_name=None,
        last_name=None,
        status="active",
        preferences={
            "default_ml_site": "MLA",
            "auto_publish": False,
            "ai_confidence_threshold": "medium",
        },
    )


@router.put(
    "/me",
    response_model=UserProfileResponse,
    responses={
        400: {"description": "Invalid input"},
        401: {"description": "Not authenticated"},
    },
)
async def update_current_user_profile(
    request: UserProfileUpdateRequest,
    current_user: CurrentUser,
) -> UserProfileResponse:
    """
    Update current user profile.

    Requires authentication via Bearer token.
    """
    # TODO: Implement user profile update service
    return UserProfileResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        first_name=request.first_name,
        last_name=request.last_name,
        status="active",
        preferences=request.preferences
        or {
            "default_ml_site": "MLA",
            "auto_publish": False,
            "ai_confidence_threshold": "medium",
        },
    )
