"""
IntelliPost AI Backend - FastAPI Application Entry Point

This module serves as the pure orchestrator entry point that creates
the FastAPI application using the application factory pattern.
Following clean architecture principles with native FastAPI DI.
"""

from api.app_factory import create_fastapi_app
from infrastructure.config.settings import Settings

# Create the FastAPI application using the application factory
settings = Settings()
app = create_fastapi_app(settings)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
