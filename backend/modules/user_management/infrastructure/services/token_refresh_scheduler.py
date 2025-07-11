"""
Token Refresh Scheduler Service for user management module.

This service implements automatic token refresh at 5.5 hours
as required by the story specifications.
"""

import asyncio
import contextlib
from datetime import UTC, datetime, timedelta
from typing import Any

from modules.user_management.domain.entities.ml_credentials import MLCredentials
from modules.user_management.domain.ports.logging.protocols import UserLoggerProtocol
from modules.user_management.domain.ports.ml_credentials_repository_protocol import (
    MLCredentialsRepositoryProtocol,
)
from modules.user_management.domain.ports.ml_oauth_service_protocol import (
    MLOAuthServiceProtocol,
)


class TokenRefreshScheduler:
    """
    Service for scheduling and executing automatic token refresh.

    Implements the critical requirement to refresh tokens at 5.5 hours
    before the 6-hour expiry time.
    """

    def __init__(
        self,
        oauth_service: MLOAuthServiceProtocol,
        credentials_repository: MLCredentialsRepositoryProtocol,
        logger: UserLoggerProtocol,
        refresh_interval_minutes: int = 30,  # Check every 30 minutes
    ):
        """
        Initialize token refresh scheduler.

        Args:
            oauth_service: ML OAuth service for token refresh
            credentials_repository: Repository for finding credentials
            logger: Logger protocol for logging operations
            refresh_interval_minutes: How often to check for tokens to refresh
        """
        self._oauth_service = oauth_service
        self._credentials_repository = credentials_repository
        self._logger = logger
        self._refresh_interval = refresh_interval_minutes * 60  # Convert to seconds
        self._running = False
        self._task: asyncio.Task[Any] | None = None

    async def start(self) -> None:
        """Start the token refresh scheduler."""
        if self._running:
            self._logger.warning("Token refresh scheduler is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_scheduler())
        self._logger.info("Token refresh scheduler started")

    async def stop(self) -> None:
        """Stop the token refresh scheduler."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        self._logger.info("Token refresh scheduler stopped")

    async def _run_scheduler(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                await self._refresh_expiring_tokens()
            except Exception as e:
                self._logger.error(f"Error in token refresh scheduler: {e}")

            # Wait for the next check interval
            await asyncio.sleep(self._refresh_interval)

    async def _refresh_expiring_tokens(self) -> None:
        """Find and refresh tokens that are approaching expiry."""
        try:
            # Find tokens that should be refreshed (at 5.5 hours before 6-hour expiry)
            refresh_threshold = datetime.now(UTC) + timedelta(
                minutes=30
            )  # 30 minutes from now

            expiring_credentials = (
                await self._credentials_repository.find_expiring_tokens(
                    refresh_threshold
                )
            )

            if not expiring_credentials:
                self._logger.debug("No tokens need refreshing at this time")
                return

            self._logger.info(
                f"Found {len(expiring_credentials)} credentials that need token refresh"
            )

            # Process each credential
            refreshed_count = 0
            failed_count = 0

            for credentials in expiring_credentials:
                try:
                    if await self._should_refresh_token(credentials):
                        await self._refresh_single_token(credentials)
                        refreshed_count += 1
                    else:
                        self._logger.debug(
                            f"Skipping refresh for credential {credentials.id}"
                        )

                except Exception as e:
                    failed_count += 1
                    self._logger.error(
                        f"Failed to refresh token for credential {credentials.id}: {e}"
                    )

                    # Mark credential as invalid if refresh fails
                    try:
                        credentials.mark_invalid(f"Automatic refresh failed: {e}")
                        await self._credentials_repository.save(credentials)
                    except Exception as save_error:
                        self._logger.error(
                            f"Failed to mark credential as invalid: {save_error}"
                        )

            if refreshed_count > 0 or failed_count > 0:
                self._logger.info(
                    f"Token refresh completed: {refreshed_count} successful, {failed_count} failed"
                )

        except Exception as e:
            self._logger.error(f"Error finding expiring tokens: {e}")

    async def _should_refresh_token(self, credentials: MLCredentials) -> bool:
        """
        Check if a token should be refreshed.

        Args:
            credentials: ML credentials to check

        Returns:
            True if token should be refreshed, False otherwise
        """
        # Skip if refresh token is expired
        if credentials.is_refresh_token_expired:
            self._logger.warning(
                f"Refresh token expired for credential {credentials.id}"
            )
            return False

        # Skip if credential is marked as invalid
        if not credentials.ml_is_valid:
            self._logger.debug(
                f"Credential {credentials.id} is marked as invalid, skipping refresh"
            )
            return False

        # Check if we're at the 5.5-hour refresh threshold
        if not credentials.should_refresh_token:
            self._logger.debug(f"Credential {credentials.id} doesn't need refresh yet")
            return False

        return True

    async def _refresh_single_token(self, credentials: MLCredentials) -> None:
        """
        Refresh a single credential's tokens.

        Args:
            credentials: ML credentials to refresh
        """
        self._logger.info(f"Refreshing tokens for credential {credentials.id}")

        try:
            # Refresh the token
            updated_credentials = await self._oauth_service.refresh_token(credentials)

            self._logger.info(
                f"Successfully refreshed tokens for credential {credentials.id}. "
                f"New expiry: {updated_credentials.ml_expires_at}"
            )

        except Exception as e:
            self._logger.error(
                f"Failed to refresh tokens for credential {credentials.id}: {e}"
            )
            raise

    async def refresh_all_eligible_tokens(self) -> int:
        """
        Manually refresh all eligible tokens.

        Returns:
            Number of tokens refreshed
        """
        return await self._oauth_service.process_expired_tokens()

    async def get_refresh_status(self) -> dict[str, Any]:
        """
        Get status information about token refresh.

        Returns:
            Status information dictionary
        """
        try:
            # Get all credentials
            now = datetime.now(UTC)

            # Find credentials needing refresh soon
            soon_threshold = now + timedelta(hours=1)  # Within 1 hour
            expiring_soon = await self._credentials_repository.find_expiring_tokens(
                soon_threshold
            )

            # Find invalid credentials
            invalid_credentials = (
                await self._credentials_repository.find_invalid_credentials()
            )

            return {
                "scheduler_running": self._running,
                "next_check_in_seconds": self._refresh_interval
                if self._running
                else None,
                "credentials_expiring_soon": len(expiring_soon),
                "invalid_credentials": len(invalid_credentials),
                "last_check_time": now.isoformat(),
            }

        except Exception as e:
            self._logger.error(f"Error getting refresh status: {e}")
            return {
                "scheduler_running": self._running,
                "error": str(e),
            }

    async def force_refresh_credential(self, credential_id: str) -> bool:
        """
        Force refresh a specific credential.

        Args:
            credential_id: UUID of credential to refresh

        Returns:
            True if refresh successful, False otherwise
        """
        try:
            from uuid import UUID

            credentials = await self._credentials_repository.find_by_id(
                UUID(credential_id)
            )
            if not credentials:
                self._logger.warning(f"Credential {credential_id} not found")
                return False

            if credentials.is_refresh_token_expired:
                self._logger.warning(
                    f"Refresh token expired for credential {credential_id}"
                )
                return False

            await self._refresh_single_token(credentials)
            return True

        except Exception as e:
            self._logger.error(
                f"Failed to force refresh credential {credential_id}: {e}"
            )
            return False

    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._running

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        """Async context manager exit."""
        await self.stop()
