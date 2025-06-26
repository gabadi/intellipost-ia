"""
IntelliPost AI Backend - FastAPI Application

This module contains the main FastAPI application with hexagonal architecture
following the specifications from Epic1.Story2.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health
from infrastructure.config.logging import (
    StructuredRequestLoggingMiddleware,
    get_logger,
    setup_logging,
)
from infrastructure.config.settings import Settings

# Initialize settings
settings = Settings()

# Setup logging
setup_logging(settings)
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

# Add request logging middleware
app.add_middleware(StructuredRequestLoggingMiddleware)

# Configure CORS using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
