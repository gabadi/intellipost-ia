"""
MercadoLibre Background Tasks Service for user management module.

This service manages background tasks for ML integration including
token refresh and connection health monitoring.
"""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
from modules.user_management.infrastructure.services.token_refresh_scheduler import (
    TokenRefreshScheduler,
)

logger = logging.getLogger(__name__)


class MLBackgroundTasksService:
    """
    Service for managing ML-related background tasks.

    Handles token refresh scheduling and other ML maintenance tasks.
    """

    def __init__(
        self,
        database_url: str | None = None,
        ml_app_id: str | None = None,
        ml_app_secret: str | None = None,
        settings: SettingsProtocol | None = None,
    ):
        """
        Initialize background tasks service.

        Args:
            database_url: Database connection URL
            ml_app_id: MercadoLibre app ID
            ml_app_secret: MercadoLibre app secret
            settings: Settings provider for configuration
        """
        # Get configuration from settings provider or use provided values
        if settings:
            self._database_url = database_url or settings.get_database_url()
            self._ml_app_id = ml_app_id or settings.ml_app_id or ""
            self._ml_app_secret = ml_app_secret or settings.ml_app_secret or ""
            is_production = settings.is_production
            environment = settings.environment
        else:
            # Fallback to direct values (for testing)
            import os

            self._database_url = database_url or os.getenv(
                "INTELLIPOST_DATABASE_URL", ""
            )
            self._ml_app_id = ml_app_id or os.getenv("INTELLIPOST_ML_APP_ID", "")
            self._ml_app_secret = ml_app_secret or os.getenv(
                "INTELLIPOST_ML_APP_SECRET", ""
            )
            is_production = (
                os.getenv("INTELLIPOST_ENVIRONMENT", "development") == "production"
            )
            environment = os.getenv("INTELLIPOST_ENVIRONMENT", "development")

        # Validate configuration (allow defaults for testing/development)
        if not self._ml_app_id or not self._ml_app_secret:
            if is_production:
                raise ValueError(
                    "ML_APP_ID and ML_APP_SECRET configuration values are required in production"
                )
            else:
                # Use test/development defaults
                self._ml_app_id = self._ml_app_id or "test_app_id"
                self._ml_app_secret = self._ml_app_secret or "test_app_secret"
                logger.info(
                    f"Using default ML credentials for {environment} environment"
                )

        # Initialize components
        self._engine = create_async_engine(self._database_url)
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

        # Services
        self._token_refresh_scheduler: TokenRefreshScheduler | None = None
        self._running = False

    async def start(self) -> None:
        """Start all background tasks."""
        if self._running:
            logger.warning("ML background tasks are already running")
            return

        try:
            logger.info("Starting ML background tasks service")

            # Initialize services
            await self._initialize_services()

            # Start token refresh scheduler
            if self._token_refresh_scheduler:
                await self._token_refresh_scheduler.start()

            self._running = True
            logger.info("ML background tasks service started successfully")

        except Exception as e:
            logger.error(f"Failed to start ML background tasks: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop all background tasks."""
        if not self._running:
            return

        try:
            logger.info("Stopping ML background tasks service")

            # Stop token refresh scheduler
            if self._token_refresh_scheduler:
                await self._token_refresh_scheduler.stop()

            # Close database connections
            await self._engine.dispose()

            self._running = False
            logger.info("ML background tasks service stopped")

        except Exception as e:
            logger.error(f"Error stopping ML background tasks: {e}")

    async def _initialize_services(self) -> None:
        """Initialize OAuth and refresh services."""
        try:
            # Create a database session for background tasks
            async with self._session_factory() as session:
                # Initialize components
                ml_client = MercadoLibreAPIClient(self._ml_app_id, self._ml_app_secret)
                credentials_repository = SQLAlchemyMLCredentialsRepository(session)
                encryption_service = CredentialEncryptionService()

                # Create OAuth service
                oauth_service = MLOAuthService(
                    ml_client=ml_client,
                    credentials_repository=credentials_repository,
                    encryption_service=encryption_service,
                    app_id=self._ml_app_id,
                    app_secret=self._ml_app_secret,
                )

                # Get refresh interval from settings
                from infrastructure.config.settings import settings

                refresh_interval = settings.ml_token_refresh_interval_minutes

                # Create token refresh scheduler
                self._token_refresh_scheduler = TokenRefreshScheduler(
                    oauth_service=oauth_service,
                    credentials_repository=credentials_repository,
                    refresh_interval_minutes=refresh_interval,
                )

        except Exception as e:
            logger.error(f"Failed to initialize ML services: {e}")
            raise

    async def get_status(self) -> dict[str, Any]:
        """
        Get status of all background tasks.

        Returns:
            Status information dictionary
        """
        try:
            status: dict[str, Any] = {
                "service_running": self._running,
                "database_connected": False,
                "token_refresh_scheduler": None,
            }

            # Check database connection
            try:
                async with self._engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                status["database_connected"] = True
            except Exception:
                status["database_connected"] = False

            # Get token refresh status
            if self._token_refresh_scheduler:
                status[
                    "token_refresh_scheduler"
                ] = await self._token_refresh_scheduler.get_refresh_status()

            return status

        except Exception as e:
            logger.error(f"Error getting background tasks status: {e}")
            return {"error": str(e)}

    async def force_token_refresh(self) -> int:
        """
        Force refresh of all eligible tokens.

        Returns:
            Number of tokens refreshed
        """
        if not self._token_refresh_scheduler:
            raise RuntimeError("Token refresh scheduler not initialized")

        return await self._token_refresh_scheduler.refresh_all_eligible_tokens()

    async def force_refresh_credential(self, credential_id: str) -> bool:
        """
        Force refresh a specific credential.

        Args:
            credential_id: UUID of credential to refresh

        Returns:
            True if refresh successful, False otherwise
        """
        if not self._token_refresh_scheduler:
            raise RuntimeError("Token refresh scheduler not initialized")

        return await self._token_refresh_scheduler.force_refresh_credential(
            credential_id
        )

    def is_running(self) -> bool:
        """Check if the service is running."""
        return self._running

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        """Async context manager exit."""
        await self.stop()


# Global instance for use in FastAPI app
_background_service: MLBackgroundTasksService | None = None


async def get_ml_background_service() -> MLBackgroundTasksService:
    """Get or create the global ML background service instance."""
    global _background_service

    if _background_service is None:
        # Use settings from infrastructure to ensure proper configuration
        from infrastructure.config.settings import settings

        _background_service = MLBackgroundTasksService(settings=settings)

    return _background_service


async def start_ml_background_tasks() -> None:
    """Start ML background tasks (called at app startup)."""
    service = await get_ml_background_service()
    await service.start()


async def stop_ml_background_tasks() -> None:
    """Stop ML background tasks (called at app shutdown)."""
    global _background_service

    if _background_service:
        await _background_service.stop()
        _background_service = None


async def get_ml_background_status() -> dict[str, Any]:
    """Get status of ML background tasks."""
    service = await get_ml_background_service()
    return await service.get_status()


async def force_ml_token_refresh() -> int:
    """Force refresh of all eligible ML tokens."""
    service = await get_ml_background_service()
    return await service.force_token_refresh()


# Example usage in FastAPI app startup/shutdown
async def ml_background_tasks_lifespan():
    """
    Example lifespan context manager for FastAPI app.

    Usage in main.py:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        await start_ml_background_tasks()
        yield
        # Shutdown
        await stop_ml_background_tasks()

    app = FastAPI(lifespan=lifespan)
    """
    try:
        await start_ml_background_tasks()
        logger.info("ML background tasks startup completed")
        yield
    finally:
        await stop_ml_background_tasks()
        logger.info("ML background tasks shutdown completed")
