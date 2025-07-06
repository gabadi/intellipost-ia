"""Dependency injection configuration for FastAPI."""

from typing import Annotated, Any

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from api.app_factory import create_fastapi_app
from infrastructure.config.logging import get_logger, setup_logging
from infrastructure.config.settings import Settings
from infrastructure.database import get_database_session
from modules.content_generation.domain.ports.ai_service_protocols import (
    AIContentServiceProtocol,
)
from modules.marketplace_integration.domain.ports.mercadolibre_service_protocol import (
    MercadoLibreServiceProtocol,
)
from modules.notifications.domain.ports.email_service_protocol import (
    EmailServiceProtocol,
)
from modules.product_management.domain.ports.product_repository_protocol import (
    ProductRepositoryProtocol,
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
from modules.user_management.domain.ports.jwt_service_protocol import (
    JWTServiceProtocol,
)
from modules.user_management.domain.ports.password_service_protocol import (
    PasswordServiceProtocol,
)
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)
from modules.user_management.domain.services.authentication import (
    AuthenticationService,
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


# Logger dependency
def get_app_logger(name: str = "main"):
    """Get application logger instance."""
    return get_logger(name)


# Type aliases for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
LoggerDep = Annotated[
    Any, Depends(get_app_logger)
]  # Will be properly typed when logger interface is defined


class DependencyContainer:
    """Container for managing service dependencies with fail-fast validation."""

    def __init__(self) -> None:
        self._user_repository: UserRepositoryProtocol | None = None
        self._product_repository: ProductRepositoryProtocol | None = None
        self._ai_content_service: AIContentServiceProtocol | None = None
        self._mercadolibre_service: MercadoLibreServiceProtocol | None = None
        self._email_service: EmailServiceProtocol | None = None
        self._password_service: PasswordServiceProtocol | None = None
        self._jwt_service: JWTServiceProtocol | None = None
        self._authentication_service: AuthenticationService | None = None
        self._register_user_use_case: RegisterUserUseCase | None = None
        self._authenticate_user_use_case: AuthenticateUserUseCase | None = None
        self._refresh_token_use_case: RefreshTokenUseCase | None = None

    # Repository registrations
    def register_user_repository(self, repository: UserRepositoryProtocol) -> None:
        """Register user repository implementation."""
        self._user_repository = repository

    def register_product_repository(
        self, repository: ProductRepositoryProtocol
    ) -> None:
        """Register product repository implementation."""
        self._product_repository = repository

    def register_ai_content_service(self, service: AIContentServiceProtocol) -> None:
        """Register AI content service implementation."""
        self._ai_content_service = service

    def register_mercadolibre_service(
        self, service: MercadoLibreServiceProtocol
    ) -> None:
        """Register MercadoLibre service implementation."""
        self._mercadolibre_service = service

    def register_email_service(self, service: EmailServiceProtocol) -> None:
        """Register email service implementation."""
        self._email_service = service

    def register_password_service(self, service: PasswordServiceProtocol) -> None:
        """Register password service implementation."""
        self._password_service = service

    def register_jwt_service(self, service: JWTServiceProtocol) -> None:
        """Register JWT service implementation."""
        self._jwt_service = service

    def register_authentication_service(self, service: AuthenticationService) -> None:
        """Register authentication service implementation."""
        self._authentication_service = service

    def register_register_user_use_case(self, use_case: RegisterUserUseCase) -> None:
        """Register user registration use case implementation."""
        self._register_user_use_case = use_case

    def register_authenticate_user_use_case(
        self, use_case: AuthenticateUserUseCase
    ) -> None:
        """Register user authentication use case implementation."""
        self._authenticate_user_use_case = use_case

    def register_refresh_token_use_case(self, use_case: RefreshTokenUseCase) -> None:
        """Register token refresh use case implementation."""
        self._refresh_token_use_case = use_case

    # Dependency providers
    def get_user_repository(self) -> UserRepositoryProtocol:
        """Get user repository dependency."""
        if self._user_repository is None:
            raise RuntimeError("User repository not registered")
        return self._user_repository

    def get_product_repository(self) -> ProductRepositoryProtocol:
        """Get product repository dependency."""
        if self._product_repository is None:
            raise RuntimeError("Product repository not registered")
        return self._product_repository

    def get_ai_content_service(self) -> AIContentServiceProtocol:
        """Get AI content service dependency."""
        if self._ai_content_service is None:
            raise RuntimeError("AI content service not registered")
        return self._ai_content_service

    def get_mercadolibre_service(self) -> MercadoLibreServiceProtocol:
        """Get MercadoLibre service dependency."""
        if self._mercadolibre_service is None:
            raise RuntimeError("MercadoLibre service not registered")
        return self._mercadolibre_service

    def get_email_service(self) -> EmailServiceProtocol:
        """Get email service dependency."""
        if self._email_service is None:
            raise RuntimeError("Email service not registered")
        return self._email_service

    def get_password_service(self) -> PasswordServiceProtocol:
        """Get password service dependency."""
        if self._password_service is None:
            raise RuntimeError("Password service not registered")
        return self._password_service

    def get_jwt_service(self) -> JWTServiceProtocol:
        """Get JWT service dependency."""
        if self._jwt_service is None:
            raise RuntimeError("JWT service not registered")
        return self._jwt_service

    def get_authentication_service(self) -> AuthenticationService:
        """Get authentication service dependency."""
        if self._authentication_service is None:
            raise RuntimeError("Authentication service not registered")
        return self._authentication_service

    def get_register_user_use_case(self) -> RegisterUserUseCase:
        """Get user registration use case dependency."""
        if self._register_user_use_case is None:
            raise RuntimeError("Register user use case not registered")
        return self._register_user_use_case

    def get_authenticate_user_use_case(self) -> AuthenticateUserUseCase:
        """Get user authentication use case dependency."""
        if self._authenticate_user_use_case is None:
            raise RuntimeError("Authenticate user use case not registered")
        return self._authenticate_user_use_case

    def get_refresh_token_use_case(self) -> RefreshTokenUseCase:
        """Get token refresh use case dependency."""
        if self._refresh_token_use_case is None:
            raise RuntimeError("Refresh token use case not registered")
        return self._refresh_token_use_case


# Global dependency container instance
container = DependencyContainer()


# FastAPI dependency functions
def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> UserRepositoryProtocol:
    """FastAPI dependency for user repository."""
    return SQLAlchemyUserRepository(session)


def get_product_repository() -> ProductRepositoryProtocol:
    """FastAPI dependency for product repository."""
    return container.get_product_repository()


def get_ai_content_service() -> AIContentServiceProtocol:
    """FastAPI dependency for AI content service."""
    return container.get_ai_content_service()


def get_mercadolibre_service() -> MercadoLibreServiceProtocol:
    """FastAPI dependency for MercadoLibre service."""
    return container.get_mercadolibre_service()


def get_email_service() -> EmailServiceProtocol:
    """FastAPI dependency for email service."""
    return container.get_email_service()


def get_password_service() -> PasswordServiceProtocol:
    """FastAPI dependency for password service."""
    return container.get_password_service()


def get_jwt_service() -> JWTServiceProtocol:
    """FastAPI dependency for JWT service."""
    return container.get_jwt_service()


def get_authentication_service() -> AuthenticationService:
    """FastAPI dependency for authentication service."""
    return container.get_authentication_service()


def get_register_user_use_case(
    user_repository: UserRepositoryProtocol = Depends(get_user_repository),
) -> RegisterUserUseCase:
    """FastAPI dependency for user registration use case."""
    authentication_service = AuthenticationService(
        user_repository=user_repository,
        password_service=container.get_password_service(),
        max_login_attempts=5,
        token_expiry_hours=24,
    )
    return RegisterUserUseCase(authentication_service)


def get_authenticate_user_use_case(
    user_repository: UserRepositoryProtocol = Depends(get_user_repository),
) -> AuthenticateUserUseCase:
    """FastAPI dependency for user authentication use case."""
    authentication_service = AuthenticationService(
        user_repository=user_repository,
        password_service=container.get_password_service(),
        max_login_attempts=5,
        token_expiry_hours=24,
    )
    return AuthenticateUserUseCase(authentication_service, container.get_jwt_service())


def get_refresh_token_use_case(
    user_repository: UserRepositoryProtocol = Depends(get_user_repository),
) -> RefreshTokenUseCase:
    """FastAPI dependency for token refresh use case."""
    return RefreshTokenUseCase(container.get_jwt_service(), user_repository)


def get_current_user(
    user_repository: UserRepositoryProtocol = Depends(get_user_repository),
):
    """FastAPI dependency for current user authentication."""
    from modules.user_management.infrastructure.middleware.auth_middleware import (
        create_auth_dependency,
    )

    return create_auth_dependency(container.get_jwt_service(), user_repository)


# Dependency type annotations for FastAPI routes
UserRepositoryDep = Annotated[UserRepositoryProtocol, Depends(get_user_repository)]
ProductRepositoryDep = Annotated[
    ProductRepositoryProtocol, Depends(get_product_repository)
]
AIContentServiceDep = Annotated[
    AIContentServiceProtocol, Depends(get_ai_content_service)
]
MercadoLibreServiceDep = Annotated[
    MercadoLibreServiceProtocol, Depends(get_mercadolibre_service)
]
EmailServiceDep = Annotated[EmailServiceProtocol, Depends(get_email_service)]
PasswordServiceDep = Annotated[PasswordServiceProtocol, Depends(get_password_service)]
JWTServiceDep = Annotated[JWTServiceProtocol, Depends(get_jwt_service)]
AuthenticationServiceDep = Annotated[
    AuthenticationService, Depends(get_authentication_service)
]
RegisterUserUseCaseDep = Annotated[
    RegisterUserUseCase, Depends(get_register_user_use_case)
]
AuthenticateUserUseCaseDep = Annotated[
    AuthenticateUserUseCase, Depends(get_authenticate_user_use_case)
]
RefreshTokenUseCaseDep = Annotated[
    RefreshTokenUseCase, Depends(get_refresh_token_use_case)
]


def create_application() -> FastAPI:
    """
    Create and configure the complete FastAPI application with all dependencies.

    This function serves as the main application factory that:
    1. Initializes settings
    2. Sets up logging
    3. Configures the DI container with authentication services
    4. Creates the FastAPI app with all dependencies wired

    Returns:
        Fully configured FastAPI application ready to run
    """
    # Initialize settings
    settings = Settings()

    # Setup logging
    setup_logging(settings)

    # Register authentication services
    password_service = BcryptPasswordService()
    jwt_service = JoseJWTService(
        secret_key=settings.user_jwt_secret_key,
        algorithm=settings.user_jwt_algorithm,
        access_token_expire_minutes=settings.user_jwt_access_token_expire_minutes,
        refresh_token_expire_days=settings.user_jwt_refresh_token_expire_days,
    )

    container.register_password_service(password_service)
    container.register_jwt_service(jwt_service)

    # Create and return the FastAPI app
    return create_fastapi_app(settings)
