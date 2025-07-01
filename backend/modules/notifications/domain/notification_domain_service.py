"""
Notification domain service protocol for shared module.

This module defines abstract base class for notification domain services.
"""

from abc import ABC, abstractmethod
from typing import Any


class NotificationDomainService(ABC):
    """Abstract base class for notification domain services."""

    @abstractmethod
    async def send_welcome_email(self, user: Any) -> bool:
        """Send welcome email to new user."""
        ...

    @abstractmethod
    async def notify_product_status_change(self, user: Any, product: Any) -> bool:
        """Notify user of product status changes."""
        ...
