"""
Auth domain user status definitions.

This module contains user status enumeration specific to the auth module,
eliminating the need to depend on the user domain module.
"""

from enum import Enum


class AuthUserStatus(Enum):
    """User account status enumeration for auth domain."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
