"""
Minimal API dependencies - only infrastructure concerns.

This module provides only the basic infrastructure dependencies needed by the API layer.
All business logic dependencies are handled in the api.dependencies module.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.settings import Settings
from infrastructure.database import get_database_session


# Settings dependency
def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Database session dependency
async def get_database_session_dep() -> AsyncGenerator[AsyncSession]:
    """Get database session dependency."""
    async for session in get_database_session():
        yield session


# Type aliases for convenience
SettingsDep = Annotated[Settings, Depends(get_settings)]
DatabaseSessionDep = Annotated[AsyncSession, Depends(get_database_session_dep)]
