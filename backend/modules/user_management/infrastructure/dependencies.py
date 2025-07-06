"""
Dependency injection providers for user management module.

This module provides concrete implementations and dependency injection
for the user management module, respecting hexagonal architecture boundaries.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.settings import settings
from infrastructure.database import get_database_session
from modules.user_management.domain.ports.settings_protocol import SettingsProtocol
from modules.user_management.infrastructure.repositories.sqlalchemy_ml_credentials_repository import (
    SQLAlchemyMLCredentialsRepository,
)
from modules.user_management.infrastructure.services.credential_encryption_service import (
    CredentialEncryptionService,
)
from modules.user_management.infrastructure.services.mercadolibre_api_client import (
    MercadoLibreAPIClient,
)
from modules.user_management.infrastructure.services.ml_oauth_service import (
    MLOAuthService,
)


def get_settings() -> SettingsProtocol:
    """Get settings instance."""
    return settings


async def get_oauth_service(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
    settings_provider: Annotated[SettingsProtocol, Depends(get_settings)],
) -> MLOAuthService:
    """Create ML OAuth service with dependencies."""
    app_id = settings_provider.ml_app_id or "test_app_id"
    app_secret = settings_provider.ml_app_secret or "test_app_secret"

    # Create dependencies
    ml_client = MercadoLibreAPIClient(app_id, app_secret)
    credentials_repository = SQLAlchemyMLCredentialsRepository(db_session)
    encryption_service = CredentialEncryptionService(settings=settings_provider)

    # Create service
    return MLOAuthService(
        ml_client=ml_client,
        credentials_repository=credentials_repository,
        encryption_service=encryption_service,
        app_id=app_id,
        app_secret=app_secret,
    )
