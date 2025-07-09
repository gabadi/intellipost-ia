"""
Content Generation infrastructure models.

This module exports all database models for the content generation module.
"""

from .generated_content_model import AIGenerationModel, GeneratedContentModel

__all__ = [
    "GeneratedContentModel",
    "AIGenerationModel",
]
