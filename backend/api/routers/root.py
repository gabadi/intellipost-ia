"""Root API router."""

from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint providing API information.

    Returns basic information about the API including message, version, and documentation URL.
    """
    return {
        "message": "IntelliPost AI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
    }
