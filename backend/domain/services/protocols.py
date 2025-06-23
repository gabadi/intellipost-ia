"""
Domain service protocols for hexagonal architecture.

This module provides a unified interface to all domain service protocols,
organized by functional modules for better maintainability.
"""

# Repository protocols (data persistence)
# AI service protocols
from .ai_service_protocols import AIContentServiceProtocol

# Domain service protocols (business logic)
from .domain_service_protocols import (
    NotificationDomainService,
    ProductDomainService,
    UserDomainService,
)

# External service protocols
from .external_service_protocols import (
    EmailServiceProtocol,
    MercadoLibreServiceProtocol,
)
from .repository_protocols import (
    ProductRepositoryProtocol,
    UserRepositoryProtocol,
)

__all__ = [
    # Repository protocols
    "ProductRepositoryProtocol",
    "UserRepositoryProtocol",
    # AI service protocols
    "AIContentServiceProtocol",
    # External service protocols
    "EmailServiceProtocol",
    "MercadoLibreServiceProtocol",
    # Domain service protocols
    "NotificationDomainService",
    "ProductDomainService",
    "UserDomainService",
]
