"""
FastAPI native dependencies for the application.

This module provides clean, simple dependency injection using FastAPI's native
Depends() system, replacing the over-engineered manual DI container.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.settings import Settings
from infrastructure.database import get_database_session

# Product management imports
from modules.product_management.application.use_cases.create_product import (
    CreateProductUseCase,
    GetProductsUseCase,
)
from modules.product_management.infrastructure.repositories.product_repository import (
    SQLAlchemyProductRepository,
)
from modules.product_management.infrastructure.services.file_storage_service import (
    FileStorageService,
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
from modules.user_management.domain.entities.user import User
from modules.user_management.domain.services.authentication import (
    AuthenticationService,
)
from modules.user_management.infrastructure.middleware.auth_middleware import (
    AuthMiddleware,
)
from modules.user_management.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from modules.user_management.infrastructure.services.bcrypt_password_service import (
    BcryptPasswordService,
)
from modules.user_management.infrastructure.services.jose_jwt_service import (
    JoseJWTService,
)


# Settings dependency
def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Infrastructure dependencies
def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyUserRepository:
    """Get user repository instance."""
    return SQLAlchemyUserRepository(session)


def get_password_service() -> BcryptPasswordService:
    """Get password service instance."""
    return BcryptPasswordService()


def get_jwt_service(settings: Settings = Depends(get_settings)) -> JoseJWTService:
    """Get JWT service instance."""
    return JoseJWTService(
        secret_key=settings.user_jwt_secret_key,
        algorithm=settings.user_jwt_algorithm,
        access_token_expire_minutes=settings.user_jwt_access_token_expire_minutes,
        refresh_token_expire_days=settings.user_jwt_refresh_token_expire_days,
    )


def get_authentication_service(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
) -> AuthenticationService:
    """Get authentication service instance."""
    return AuthenticationService(
        user_repository=user_repository,
        password_service=password_service,
        max_login_attempts=5,
        token_expiry_hours=24,
    )


# Use case dependencies
def get_register_user_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> RegisterUserUseCase:
    """Get user registration use case instance."""
    return RegisterUserUseCase(auth_service)


def get_authenticate_user_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),
    jwt_service: JoseJWTService = Depends(get_jwt_service),
) -> AuthenticateUserUseCase:
    """Get user authentication use case instance."""
    return AuthenticateUserUseCase(auth_service, jwt_service)


def get_refresh_token_use_case(
    jwt_service: JoseJWTService = Depends(get_jwt_service),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> RefreshTokenUseCase:
    """Get token refresh use case instance."""
    return RefreshTokenUseCase(jwt_service, user_repository)


# Initialize the HTTPBearer security scheme
security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    jwt_service: JoseJWTService = Depends(get_jwt_service),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> User:
    """Get current authenticated user."""
    auth_middleware = AuthMiddleware(jwt_service, user_repository)
    return await auth_middleware.get_current_user(credentials)


def get_current_user_factory():
    """Factory function for current user dependency - matches old DI pattern."""
    return Depends(get_current_user)


# Type aliases for convenience
SettingsDep = Annotated[Settings, Depends(get_settings)]
UserRepositoryDep = Annotated[SQLAlchemyUserRepository, Depends(get_user_repository)]
PasswordServiceDep = Annotated[BcryptPasswordService, Depends(get_password_service)]
JWTServiceDep = Annotated[JoseJWTService, Depends(get_jwt_service)]
AuthServiceDep = Annotated[AuthenticationService, Depends(get_authentication_service)]
RegisterUseCaseDep = Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)]
AuthenticateUseCaseDep = Annotated[
    AuthenticateUserUseCase, Depends(get_authenticate_user_use_case)
]
RefreshTokenUseCaseDep = Annotated[
    RefreshTokenUseCase, Depends(get_refresh_token_use_case)
]


# Product management dependencies
def get_product_repository(
    session: AsyncSession = Depends(get_database_session),
) -> SQLAlchemyProductRepository:
    """Get product repository instance."""
    return SQLAlchemyProductRepository(session)


def get_file_storage_service(
    settings: Settings = Depends(get_settings),
) -> FileStorageService:
    """Get file storage service instance."""
    return FileStorageService(settings)


def get_create_product_use_case(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository),
    file_storage_service: FileStorageService = Depends(get_file_storage_service),
) -> CreateProductUseCase:
    """Get create product use case instance."""
    return CreateProductUseCase(product_repository, file_storage_service)


def get_get_products_use_case(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository),
) -> GetProductsUseCase:
    """Get products use case instance."""
    return GetProductsUseCase(product_repository)


# Product management type aliases
ProductRepositoryDep = Annotated[
    SQLAlchemyProductRepository, Depends(get_product_repository)
]
FileStorageServiceDep = Annotated[FileStorageService, Depends(get_file_storage_service)]
CreateProductUseCaseDep = Annotated[
    CreateProductUseCase, Depends(get_create_product_use_case)
]
GetProductsUseCaseDep = Annotated[
    GetProductsUseCase, Depends(get_get_products_use_case)
]
