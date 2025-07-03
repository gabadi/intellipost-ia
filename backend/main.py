"""
IntelliPost AI Backend - FastAPI Application Entry Point

This module serves as the pure orchestrator entry point that creates
the FastAPI application using the dependency injection container.
Following the Application Factory Pattern for clean architecture.
"""

from di.container import create_application

# Create the FastAPI application using the application factory
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
