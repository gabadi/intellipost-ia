"""
Product Management Module

This module defines product-related entities and protocols.
It defines what it needs from external entities via protocols
but doesn't import those entities directly.
"""

from .protocols import OwnerProtocol, ManagerProtocol
from .product import Product

__all__ = ["OwnerProtocol", "ManagerProtocol", "Product"]