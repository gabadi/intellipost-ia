"""
FastAPI application factory with correct protocol architecture.

This factory creates the FastAPI application and wires all dependencies
using the correct protocol architecture where API owns its protocols.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth_router
from infrastructure.config.logging import setup_logging
from infrastructure.config.settings import Settings


def create_fastapi_app(settings: Settings) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        settings: Application settings

    Returns:
        Configured FastAPI application
    """

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        """
        Handle application lifespan events.

        Args:
            _app: FastAPI application instance
        """
        # Startup
        setup_logging(settings)
        yield
        # Shutdown (add cleanup logic here if needed)

    # Create FastAPI app with lifespan
    app = FastAPI(
        title="IntelliPost API",
        description="AI-powered content generation and marketplace integration platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router.router, prefix="/api/v1")

    return app


def create_application() -> FastAPI:
    """
    Create the complete application with all dependencies.

    Returns:
        Configured FastAPI application
    """
    settings = Settings()
    return create_fastapi_app(settings)
