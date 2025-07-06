"""
SQLAlchemy ML Credentials Repository implementation for user management module.

This module implements the ML credentials repository using SQLAlchemy
following the hexagonal architecture pattern.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user_management.domain.entities.ml_credentials import MLCredentials
from modules.user_management.domain.ports.ml_credentials_repository_protocol import (
    MLCredentialsRepositoryProtocol,
)
from modules.user_management.infrastructure.models.ml_credentials_model import (
    MLCredentialsModel,
)


class SQLAlchemyMLCredentialsRepository(MLCredentialsRepositoryProtocol):
    """
    SQLAlchemy implementation of ML credentials repository.
    
    Implements the MLCredentialsRepositoryProtocol using SQLAlchemy
    for ML credentials persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, credentials: MLCredentials) -> None:
        """Save or update ML credentials."""
        try:
            # Check if credentials already exist
            existing = await self._session.get(MLCredentialsModel, credentials.id)
            
            if existing:
                # Update existing credentials
                existing.update_from_domain(credentials)
                await self._session.flush()
            else:
                # Create new credentials
                model = MLCredentialsModel.from_domain(credentials)
                self._session.add(model)
                await self._session.flush()
                
        except Exception as e:
            await self._session.rollback()
            raise RuntimeError(f"Failed to save ML credentials: {str(e)}") from e

    async def find_by_user_id(self, user_id: UUID) -> Optional[MLCredentials]:
        """Find ML credentials by user ID."""
        try:
            stmt = select(MLCredentialsModel).where(
                MLCredentialsModel.user_id == user_id
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return model.to_domain() if model else None
            
        except Exception as e:
            raise RuntimeError(f"Failed to find ML credentials by user ID: {str(e)}") from e

    async def find_by_id(self, credentials_id: UUID) -> Optional[MLCredentials]:
        """Find ML credentials by ID."""
        try:
            model = await self._session.get(MLCredentialsModel, credentials_id)
            return model.to_domain() if model else None
            
        except Exception as e:
            raise RuntimeError(f"Failed to find ML credentials by ID: {str(e)}") from e

    async def delete_by_user_id(self, user_id: UUID) -> bool:
        """Delete ML credentials by user ID."""
        try:
            stmt = delete(MLCredentialsModel).where(
                MLCredentialsModel.user_id == user_id
            )
            result = await self._session.execute(stmt)
            await self._session.flush()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self._session.rollback()
            raise RuntimeError(f"Failed to delete ML credentials: {str(e)}") from e

    async def find_expiring_tokens(self, before: datetime) -> List[MLCredentials]:
        """Find credentials with access tokens expiring before specified time."""
        try:
            stmt = select(MLCredentialsModel).where(
                MLCredentialsModel.ml_expires_at <= before,
                MLCredentialsModel.ml_is_valid == True
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            
            return [model.to_domain() for model in models]
            
        except Exception as e:
            raise RuntimeError(f"Failed to find expiring tokens: {str(e)}") from e

    async def find_by_site_id(self, site_id: str) -> List[MLCredentials]:
        """Find credentials by MercadoLibre site ID."""
        try:
            stmt = select(MLCredentialsModel).where(
                MLCredentialsModel.ml_site_id == site_id
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            
            return [model.to_domain() for model in models]
            
        except Exception as e:
            raise RuntimeError(f"Failed to find credentials by site ID: {str(e)}") from e

    async def find_invalid_credentials(self) -> List[MLCredentials]:
        """Find credentials marked as invalid."""
        try:
            stmt = select(MLCredentialsModel).where(
                MLCredentialsModel.ml_is_valid == False
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            
            return [model.to_domain() for model in models]
            
        except Exception as e:
            raise RuntimeError(f"Failed to find invalid credentials: {str(e)}") from e

    async def count_by_user_id(self, user_id: UUID) -> int:
        """Count ML credentials for a user."""
        try:
            stmt = select(func.count(MLCredentialsModel.id)).where(
                MLCredentialsModel.user_id == user_id
            )
            result = await self._session.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            raise RuntimeError(f"Failed to count ML credentials: {str(e)}") from e

    async def exists_by_user_id(self, user_id: UUID) -> bool:
        """Check if ML credentials exist for a user."""
        try:
            count = await self.count_by_user_id(user_id)
            return count > 0
            
        except Exception as e:
            raise RuntimeError(f"Failed to check ML credentials existence: {str(e)}") from e

    async def update_validation_status(
        self, 
        credentials_id: UUID, 
        is_valid: bool, 
        error: Optional[str] = None
    ) -> bool:
        """Update validation status of ML credentials."""
        try:
            stmt = update(MLCredentialsModel).where(
                MLCredentialsModel.id == credentials_id
            ).values(
                ml_is_valid=is_valid,
                ml_validation_error=error,
                ml_last_validated_at=datetime.now(),
                updated_at=datetime.now()
            )
            result = await self._session.execute(stmt)
            await self._session.flush()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self._session.rollback()
            raise RuntimeError(f"Failed to update validation status: {str(e)}") from e

    async def clear_pkce_parameters(self, credentials_id: UUID) -> bool:
        """Clear PKCE parameters after OAuth flow completion."""
        try:
            stmt = update(MLCredentialsModel).where(
                MLCredentialsModel.id == credentials_id
            ).values(
                pkce_code_challenge=None,
                pkce_code_verifier=None,
                updated_at=datetime.now()
            )
            result = await self._session.execute(stmt)
            await self._session.flush()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self._session.rollback()
            raise RuntimeError(f"Failed to clear PKCE parameters: {str(e)}") from e

    async def find_by_ml_user_id(self, ml_user_id: int) -> Optional[MLCredentials]:
        """Find ML credentials by MercadoLibre user ID."""
        try:
            stmt = select(MLCredentialsModel).where(
                MLCredentialsModel.ml_user_id == ml_user_id
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return model.to_domain() if model else None
            
        except Exception as e:
            raise RuntimeError(f"Failed to find ML credentials by ML user ID: {str(e)}") from e