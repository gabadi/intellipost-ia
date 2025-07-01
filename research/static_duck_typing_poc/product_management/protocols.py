"""
Protocol definitions for product management.

This module defines protocols that specify the interface requirements
for external entities without importing those entities directly.
This enables static duck typing and loose coupling.
"""

from typing import Protocol
from uuid import UUID


class OwnerProtocol(Protocol):
    """
    Protocol defining the interface required for product owners.
    
    Any entity that provides these methods can be used as a product owner,
    regardless of its actual type. This enables structural subtyping
    and module independence.
    """
    
    def get_id(self) -> UUID:
        """Get the owner's unique identifier."""
        ...
    
    def get_name(self) -> str:
        """Get the owner's display name."""
        ...
    
    def get_email(self) -> str:
        """Get the owner's email address."""
        ...


class ManagerProtocol(Protocol):
    """
    Protocol for entities that can manage products.
    
    This is a more complex protocol to test multiple method requirements.
    """
    
    def get_id(self) -> UUID:
        """Get the manager's unique identifier."""
        ...
    
    def get_name(self) -> str:
        """Get the manager's display name."""
        ...
    
    def activate(self) -> None:
        """Activate the manager."""
        ...
    
    def deactivate(self) -> None:
        """Deactivate the manager."""
        ...
    
    @property
    def is_active(self) -> bool:
        """Check if the manager is active."""
        ...