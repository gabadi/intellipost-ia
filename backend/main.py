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
from infrastructure.middleware import CSRFMiddleware, RateLimitMiddleware
from infrastructure.redis_client import RedisClient
from modules.auth.api.router import router as auth_router
from modules.user.api.router import router as user_router

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

    # Initialize Redis connection
    try:
        redis_client = await RedisClient.get_client()
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        if settings.is_production:
            raise

    yield

    # Shutdown
    logger.info("Shutting down IntelliPost AI Backend...")
    await RedisClient.close()


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
app.include_router(user_router)

# Add middleware in correct order (last added = first executed)
# 1. CORS (needs to be outermost for preflight requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Request logging
app.add_middleware(StructuredRequestLoggingMiddleware)

# 3. Rate limiting (Redis-based distributed)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=10)

# 4. CSRF protection for cookie-based auth
if settings.is_production:
    app.add_middleware(
        CSRFMiddleware,
        exclude_paths={
            "/health",
            "/health/ready",
            "/health/live",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
        },
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
