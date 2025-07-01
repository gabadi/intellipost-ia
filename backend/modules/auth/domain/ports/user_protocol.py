"""User protocol for authentication module to interact with user entities."""

from datetime import datetime
from typing import Protocol
from uuid import UUID


class UserProtocol(Protocol):
    """Protocol defining the interface for user entities in authentication context."""

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None

    def activate(self) -> None:
        """Activate user account."""
        ...

    def deactivate(self) -> None:
        """Deactivate user account."""
        ...

    def verify_email(self) -> None:
        """Mark user's email as verified."""
        ...

    def record_login(self) -> None:
        """Record user login timestamp."""
        ...
