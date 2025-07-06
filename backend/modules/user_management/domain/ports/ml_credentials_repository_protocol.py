"""
MercadoLibre Credentials Repository Protocol for user management module.

This module defines the protocol for ML credentials repository operations
following the hexagonal architecture pattern.
"""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from modules.user_management.domain.entities.ml_credentials import MLCredentials


class MLCredentialsRepositoryProtocol(Protocol):
    """
    Protocol for MercadoLibre credentials repository operations.

    Defines the interface for ML credentials persistence following
    the hexagonal architecture pattern and protocol-based design.
    """

    async def save(self, credentials: MLCredentials) -> None:
        """
        Save or update ML credentials.

        Args:
            credentials: ML credentials entity to save

        Raises:
            RepositoryError: If save operation fails
        """
        ...

    async def find_by_user_id(self, user_id: UUID) -> MLCredentials | None:
        """
        Find ML credentials by user ID.

        Args:
            user_id: User UUID to search for

        Returns:
            MLCredentials entity if found, None otherwise

        Raises:
            RepositoryError: If search operation fails
        """
        ...

    async def find_by_id(self, credentials_id: UUID) -> MLCredentials | None:
        """
        Find ML credentials by ID.

        Args:
            credentials_id: Credentials UUID to search for

        Returns:
            MLCredentials entity if found, None otherwise

        Raises:
            RepositoryError: If search operation fails
        """
        ...

    async def delete_by_user_id(self, user_id: UUID) -> bool:
        """
        Delete ML credentials by user ID.

        Args:
            user_id: User UUID to delete credentials for

        Returns:
            True if credentials were deleted, False if not found

        Raises:
            RepositoryError: If delete operation fails
        """
        ...

    async def find_expiring_tokens(self, before: datetime) -> list[MLCredentials]:
        """
        Find credentials with access tokens expiring before specified time.

        Used for automatic token refresh scheduling at 5.5 hours.

        Args:
            before: Datetime to check expiration against

        Returns:
            List of MLCredentials entities with expiring tokens

        Raises:
            RepositoryError: If search operation fails
        """
        ...

    async def find_by_site_id(self, site_id: str) -> list[MLCredentials]:
        """
        Find credentials by MercadoLibre site ID.

        Args:
            site_id: MercadoLibre site ID (MLA, MLM, MBL, MLC, MCO)

        Returns:
            List of MLCredentials entities for the site

        Raises:
            RepositoryError: If search operation fails
        """
        ...

    async def find_invalid_credentials(self) -> list[MLCredentials]:
        """
        Find credentials marked as invalid.

        Used for connection health monitoring and cleanup.

        Returns:
            List of MLCredentials entities marked as invalid

        Raises:
            RepositoryError: If search operation fails
        """
        ...

    async def count_by_user_id(self, user_id: UUID) -> int:
        """
        Count ML credentials for a user.

        Args:
            user_id: User UUID to count credentials for

        Returns:
            Number of credentials found for the user

        Raises:
            RepositoryError: If count operation fails
        """
        ...

    async def exists_by_user_id(self, user_id: UUID) -> bool:
        """
        Check if ML credentials exist for a user.

        Args:
            user_id: User UUID to check

        Returns:
            True if credentials exist, False otherwise

        Raises:
            RepositoryError: If check operation fails
        """
        ...

    async def update_validation_status(
        self, credentials_id: UUID, is_valid: bool, error: str | None = None
    ) -> bool:
        """
        Update validation status of ML credentials.

        Args:
            credentials_id: Credentials UUID to update
            is_valid: Whether credentials are valid
            error: Error message if invalid

        Returns:
            True if update successful, False if not found

        Raises:
            RepositoryError: If update operation fails
        """
        ...

    async def clear_pkce_parameters(self, credentials_id: UUID) -> bool:
        """
        Clear PKCE parameters after OAuth flow completion.

        Args:
            credentials_id: Credentials UUID to clear PKCE for

        Returns:
            True if cleared successfully, False if not found

        Raises:
            RepositoryError: If clear operation fails
        """
        ...

    async def find_by_ml_user_id(self, ml_user_id: int) -> MLCredentials | None:
        """
        Find ML credentials by MercadoLibre user ID.

        Args:
            ml_user_id: MercadoLibre user ID

        Returns:
            MLCredentials entity if found, None otherwise

        Raises:
            RepositoryError: If search operation fails
        """
        ...
