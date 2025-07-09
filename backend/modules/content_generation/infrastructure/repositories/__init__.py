"""
Content Generation infrastructure repositories.

This module exports all repositories for the content generation module.
"""

from .sqlalchemy_content_repository import SQLAlchemyContentRepository

__all__ = [
    "SQLAlchemyContentRepository",
]
