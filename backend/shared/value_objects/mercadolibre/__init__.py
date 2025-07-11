"""
MercadoLibre specific value objects.

This module provides value objects that model MercadoLibre-specific
data structures and enforce their validation rules.
"""

from .attributes import MLAttributes
from .sale_terms import MLSaleTerms
from .shipping import MLShipping

__all__ = [
    "MLAttributes",
    "MLSaleTerms",
    "MLShipping",
]
