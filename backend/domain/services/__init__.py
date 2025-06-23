"""Domain services module."""

from .protocols import (
    AIContentServiceProtocol,
    EmailServiceProtocol,
    MercadoLibreServiceProtocol,
    NotificationDomainService,
    ProductDomainService,
    ProductRepositoryProtocol,
    UserDomainService,
    UserRepositoryProtocol,
)

__all__ = [
    "AIContentServiceProtocol",
    "EmailServiceProtocol",
    "MercadoLibreServiceProtocol",
    "NotificationDomainService",
    "ProductDomainService",
    "ProductRepositoryProtocol",
    "UserDomainService",
    "UserRepositoryProtocol",
]
