"""
Application Factory for FastAPI.

This module contains the application factory pattern implementation
that isolates FastAPI app creation from the main entry point.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health
from infrastructure.config.logging import (
    StructuredRequestLoggingMiddleware,
    get_logger,
)
from infrastructure.config.settings import Settings
from infrastructure.middleware.security_middleware import create_security_middleware
from modules.user_management.api.routers.auth_router import router as auth_router


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

        yield

        # Shutdown
        logger.info("Shutting down IntelliPost AI Backend...")

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
    app.include_router(auth_router)

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add security middleware (HTTPS, security headers)
    security_middleware = create_security_middleware(settings)
    for middleware_class, middleware_kwargs in security_middleware:
        app.add_middleware(middleware_class, **middleware_kwargs)

    # Add request logging middleware
    app.add_middleware(StructuredRequestLoggingMiddleware)

    # Add rate limiting middleware for auth endpoints
    # TODO: Temporarily disabled for debugging
    # app.add_middleware(
    #     AuthRateLimitMiddleware,
    #     max_requests=5,  # 5 requests per minute as per requirements
    #     window_minutes=1
    # )

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

    @app.get("/security-status")
    async def security_status() -> dict[str, bool | str]:  # type: ignore[reportUnusedFunction]
        """
        Security configuration status endpoint.

        Returns:
            Dict containing security configuration status.
        """
        return {
            "environment": settings.environment,
            "https_only": settings.https_only,
            "secure_cookies": settings.secure_cookies,
            "hsts_enabled": settings.https_only,
            "security_headers_enabled": True,
        }

    return app
