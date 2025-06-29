"""
Dependency injection containers for auth module.

This module provides simple dependency injection functions for creating
auth-related service instances with their dependencies properly configured.
"""

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
from modules.user.infrastructure.user_repository import UserRepository


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
