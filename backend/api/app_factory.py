"""
Application Factory for FastAPI.

This module contains the application factory pattern implementation
that isolates FastAPI app creation from the main entry point.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import (
    create_auth_router_factory,
    create_content_generation_router_factory,
    create_product_router_factory,
    create_user_router_factory,
    get_ml_oauth_router,
    start_ml_background_tasks,
    stop_ml_background_tasks,
)
from api.routers import health
from api.routers.config import create_config_router
from infrastructure.config.logging import (
    StructuredRequestLoggingMiddleware,
    get_logger,
)
from infrastructure.config.settings import Settings
from infrastructure.middleware.security_middleware import (
    RateLimitMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)


def create_fastapi_app(settings: Settings) -> FastAPI:
    """
    Create and configure a FastAPI application instance.

    Args:
        settings: Application settings instance

    Returns:
        Configured FastAPI application
    """
    logger = get_logger(__name__)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        """Application lifespan event handler."""
        # Startup
        logger.info("Starting IntelliPost AI Backend...")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")

        # Seed database with default data
        try:
            from infrastructure.seed import seed_database

            await seed_database(settings)
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            raise

        # Start MercadoLibre background tasks (including token refresh scheduler)
        try:
            await start_ml_background_tasks()
            logger.info("MercadoLibre background tasks started successfully")

        except Exception as e:
            logger.error(f"Failed to start MercadoLibre background tasks: {e}")
            raise

        yield

        # Shutdown
        logger.info("Shutting down IntelliPost AI Backend...")

        # Stop MercadoLibre background tasks
        try:
            await stop_ml_background_tasks()
            logger.info("MercadoLibre background tasks stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping MercadoLibre background tasks: {e}")

    # Create FastAPI application
    app = FastAPI(
        title="IntelliPost AI Backend",
        version="1.0.0",
        description="Intelligent social media posting platform with AI content generation",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Include routers
    app.include_router(health.router)

    # Create and include configuration router
    config_router = create_config_router(settings)
    app.include_router(config_router)

    # Create and include authentication router
    auth_router = create_auth_router_factory(
        access_token_expire_minutes=settings.user_jwt_access_token_expire_minutes,
        registration_enabled=settings.user_registration_enabled,
    )
    app.include_router(auth_router)

    # Create and include user router
    user_router = create_user_router_factory()
    app.include_router(user_router)

    # Create and include product router
    product_router = create_product_router_factory()
    app.include_router(product_router)

    # Create and include content generation router
    content_generation_router = create_content_generation_router_factory()
    app.include_router(content_generation_router)

    # Include MercadoLibre OAuth router
    ml_oauth_router = get_ml_oauth_router()
    app.include_router(ml_oauth_router)

    # Configure CORS middleware with secure settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,  # Required for JWT tokens in cookies
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
        ],
        expose_headers=["X-Total-Count"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )

    # Add security middleware (order matters!)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        RateLimitMiddleware, requests_per_minute=120, auth_requests_per_minute=5
    )
    app.add_middleware(RequestValidationMiddleware, max_request_size=10 * 1024 * 1024)

    # Add request logging middleware (last to capture all requests)
    app.add_middleware(StructuredRequestLoggingMiddleware)

    @app.get("/")
    async def root() -> dict[str, str]:  # type: ignore[reportUnusedFunction]
        """
        Root endpoint providing basic API information.

        Returns:
            Dict containing API information.
        """
        return {
            "message": "IntelliPost AI Backend API",
            "version": "1.0.0",
            "docs": "/docs",
        }

    return app
