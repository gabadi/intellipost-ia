"""
User status definitions.

This module contains the user status enumeration and related logic.
"""

from enum import Enum


class UserStatus(Enum):
    """User account status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
