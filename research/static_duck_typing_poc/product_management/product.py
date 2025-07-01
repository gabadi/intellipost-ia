"""
Product entity definition.

This module defines the Product class that uses protocols
to specify requirements for external dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from .protocols import OwnerProtocol, ManagerProtocol


@dataclass
class Product:
    """
    Product entity that uses protocols for external dependencies.
    
    This class depends on OwnerProtocol and ManagerProtocol
    but doesn't import concrete implementations.
    """
    
    id: UUID
    name: str
    description: str
    owner: OwnerProtocol  # Uses protocol, not concrete type
    created_at: datetime
    manager: ManagerProtocol | None = None
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        owner: OwnerProtocol,  # Accepts any object matching the protocol
        manager: ManagerProtocol | None = None,
    ) -> "Product":
        """Create a new product instance."""
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            owner=owner,
            created_at=datetime.now(),
            manager=manager,
        )
    
    def get_owner_info(self) -> dict[str, str]:
        """Get information about the product owner."""
        return {
            "id": str(self.owner.get_id()),
            "name": self.owner.get_name(),
            "email": self.owner.get_email(),
        }
    
    def assign_manager(self, manager: ManagerProtocol) -> None:
        """Assign a manager to the product."""
        if not manager.is_active:
            raise ValueError("Cannot assign inactive manager")
        self.manager = manager
    
    def get_manager_info(self) -> dict[str, str] | None:
        """Get information about the product manager."""
        if self.manager is None:
            return None
        
        return {
            "id": str(self.manager.get_id()),
            "name": self.manager.get_name(),
            "active": str(self.manager.is_active),
        }
    
    def __str__(self) -> str:
        """String representation of the product."""
        return f"Product(id={self.id}, name={self.name}, owner={self.owner.get_name()})"