"""
Email service protocol for hexagonal architecture.

This module defines Protocol interface for email notification services,
ensuring loose coupling between domain logic and external services.

Architectural Decision: Protocol in Domain Layer
==============================================

**PR Review Question**: "This is not a port? why in domain?"

**Answer**: This IS a port (Protocol interface) and correctly belongs in domain:

1. **Port Definition**: In hexagonal architecture, ports are interfaces defined by the domain
2. **Business Needs**: Domain defines what email capabilities it needs
3. **Implementation Agnostic**: Domain doesn't care if emails are sent via SMTP, SendGrid, or SES
4. **Dependency Direction**: Infrastructure implements this protocol, not the other way around
5. **Testing Benefits**: Domain can be tested with mock implementations

Hexagonal Architecture Pattern:
```
Domain Layer (Core Business Logic)
├── Entities
├── Value Objects
├── Business Rules
└── Ports (Protocols) <- THIS FILE

Infrastructure Layer
└── Adapters (Implementations) <- implements the protocols
```

The protocol IS the port - it defines the contract that infrastructure must fulfill.
"""

from typing import Any, Protocol


class EmailServiceProtocol(Protocol):
    """Protocol for email notification services."""

    async def send_verification_email(self, user: Any, verification_link: str) -> bool:
        """Send email verification message."""
        ...

    async def send_notification(self, user: Any, subject: str, content: str) -> bool:
        """Send general notification email."""
        ...

    async def send_product_published_notification(
        self, user: Any, product: Any
    ) -> bool:
        """Send notification when product is published."""
        ...
