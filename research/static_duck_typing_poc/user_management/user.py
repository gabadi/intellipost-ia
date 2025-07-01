"""
User entity definition.

This module defines the User class with no knowledge of external protocols.
The User class implements methods and properties that might coincidentally
match protocol requirements defined elsewhere.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class User:
    """
    User entity representing a system user.
    
    This class has no knowledge of any protocols but implements
    methods that might be required by external interfaces.
    """
    
    id: UUID
    email: str
    name: str
    created_at: datetime
    is_active: bool = True
    
    @classmethod
    def create(cls, email: str, name: str) -> "User":
        """Create a new user instance."""
        return cls(
            id=uuid4(),
            email=email,
            name=name,
            created_at=datetime.now(),
            is_active=True
        )
    
    def get_id(self) -> UUID:
        """Get the user's unique identifier."""
        return self.id
    
    def get_name(self) -> str:
        """Get the user's display name."""
        return self.name
    
    def get_email(self) -> str:
        """Get the user's email address."""
        return self.email
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"User(id={self.id}, name={self.name}, email={self.email})"