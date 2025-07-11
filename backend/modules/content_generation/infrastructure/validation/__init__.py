"""
Infrastructure validation module for content generation.

This module provides runtime validation tools to ensure type safety
and prevent architectural violations across service layers.
"""

from .type_safety_validator import TypeSafetyValidator

__all__ = ["TypeSafetyValidator"]
