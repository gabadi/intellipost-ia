"""
IntelliPost AI Backend - FastAPI Application

This module contains the main FastAPI application with hexagonal architecture
following the specifications from Epic1.Story2.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health
from infrastructure.config.logging import (
    RequestLoggingMiddleware,
    get_logger,
    setup_logging,
)
from infrastructure.config.settings import Settings

# Initialize settings
settings = Settings()

# Setup logging
setup_logging(settings)
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="IntelliPost AI Backend",
    version="1.0.0",
    description="Intelligent social media posting platform with AI content generation",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(health.router)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Application startup event handler."""
    logger.info("Starting IntelliPost AI Backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Application shutdown event handler."""
    logger.info("Shutting down IntelliPost AI Backend...")


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
