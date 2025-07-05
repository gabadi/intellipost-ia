"""
Factory for creating enhanced authentication service instances.

This module provides a factory function to create and wire the enhanced authentication
service with all its dependencies, making it ready to satisfy the API protocol.
"""

from infrastructure.database import get_database_session
from modules.user_management.domain.services.enhanced_authentication import (
    EnhancedAuthenticationService,
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


async def create_enhanced_authentication_service() -> EnhancedAuthenticationService:
    """
    Factory function to create EnhancedAuthenticationService with all dependencies.

    This function creates and wires all the internal dependencies needed
    by the enhanced authentication service, making it ready to satisfy
    the API AuthenticationProviderProtocol through duck typing.

    Returns:
        EnhancedAuthenticationService instance ready to use
    """
    # Create database session using the async generator properly
    session_generator = get_database_session()
    session = await anext(session_generator)

    # Create repositories
    user_repository = UserRepository(session)
    refresh_token_repository = RefreshTokenRepository(session)

    # Create services
    password_service = PasswordService()
    jwt_service = JWTService()

    # Create and return the enhanced authentication service
    return EnhancedAuthenticationService(
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service,
        refresh_token_repository=refresh_token_repository,
        max_login_attempts=5,
        token_expiry_hours=24,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )
