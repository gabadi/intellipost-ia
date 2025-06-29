"""
Dependency injection containers for auth module.

This module provides simple dependency injection functions for creating
auth-related service instances with their dependencies properly configured.
"""

import logging
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.settings import Settings
from infrastructure.database import get_database_session
from modules.auth.application.authentication_service import AuthenticationService
from modules.auth.domain.protocols import AuthenticationServiceProtocol
from modules.auth.infrastructure.jwt_service import JWTService
from modules.auth.infrastructure.password_service import PasswordService
from modules.user.application.user_service import UserService
from modules.user.domain.exceptions import UserAlreadyExistsError
from modules.user.domain.user_status import UserStatus
from modules.user.infrastructure.user_repository import UserRepository

logger = logging.getLogger(__name__)


@dataclass
class DefaultUserCreationRequest:
    """Request object for creating default users."""

    email: str
    password_hash: str
    first_name: str | None
    last_name: str | None
    status: UserStatus


def get_user_service(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
):
    """
    Create user service with database session.

    Args:
        db_session: Database session dependency

    Returns:
        UserService: Configured user service
    """
    user_repository = UserRepository(db_session)
    return UserService(user_repository)


def get_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
    settings: Annotated[Settings, Depends(lambda: Settings())],
) -> AuthenticationServiceProtocol:
    """
    Create authentication service with protocol-based dependencies.

    Args:
        user_service: User service dependency (protocol-based)
        settings: Application settings dependency

    Returns:
        AuthenticationServiceProtocol: Configured authentication service
    """
    # Create supporting services
    password_service = PasswordService()
    jwt_service = JWTService(settings)

    # Create authentication service with protocol-based user service
    return AuthenticationService(user_service, password_service, jwt_service)


async def initialize_default_users(settings: Settings) -> None:
    """
    Initialize default users during application startup.

    Args:
        settings: Application settings containing default user configuration
    """
    logger.info("Starting default user initialization...")

    try:
        # Create a database session for user initialization
        from infrastructure.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db_session:
            # Create services with dependency injection
            user_repository = UserRepository(db_session)
            user_service = UserService(user_repository)
            password_service = PasswordService()

            # Initialize default admin user
            await _create_default_admin_user(
                user_service=user_service,
                password_service=password_service,
                settings=settings,
            )

        logger.info("Default user initialization completed successfully")

    except Exception as e:
        logger.error(f"Failed to initialize default users: {str(e)}")
        raise


async def _create_default_admin_user(
    user_service: UserService,
    password_service: PasswordService,
    settings: Settings,
) -> None:
    """
    Create the default admin user if it doesn't exist.

    Args:
        user_service: Service for user operations
        password_service: Service for password hashing
        settings: Application settings
    """
    admin_email = settings.default_admin_email.lower().strip()

    # Check if admin user already exists
    existing_user = await user_service.get_user_by_email(admin_email)
    if existing_user:
        logger.info(
            f"Default admin user already exists: {admin_email}",
            extra={
                "user_id": str(existing_user.id),
                "email": admin_email,
                "is_active": existing_user.is_active,
                "created_at": existing_user.created_at.isoformat(),
            },
        )
        return

    # Create admin user
    try:
        # Hash the default password
        password_hash = password_service.hash_password(settings.default_admin_password)

        # Create user creation request
        user_request = DefaultUserCreationRequest(
            email=admin_email,
            password_hash=password_hash,
            first_name=settings.default_admin_first_name,
            last_name=settings.default_admin_last_name,
            status=UserStatus.ACTIVE,
        )

        # Create the user
        created_user = await user_service.create_user(user_request)

        logger.info(
            f"Default admin user created successfully: {admin_email}",
            extra={
                "user_id": str(created_user.id),
                "email": admin_email,
                "is_active": created_user.is_active,
                "created_at": created_user.created_at.isoformat(),
                "security_context": "default_user_creation",
            },
        )

    except UserAlreadyExistsError:
        # Handle race condition - another instance created the user
        logger.info(
            f"Default admin user already exists (race condition): {admin_email}",
            extra={
                "email": admin_email,
                "security_context": "default_user_creation_race_condition",
            },
        )
    except Exception as e:
        logger.error(
            f"Failed to create default admin user: {admin_email}",
            extra={
                "email": admin_email,
                "error": str(e),
                "error_type": type(e).__name__,
                "security_context": "default_user_creation_failed",
            },
        )
        raise
