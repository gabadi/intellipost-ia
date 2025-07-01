"""
Authentication domain service for user management.

This module contains pure business logic for user authentication operations.
"""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from modules.user_management.domain.entities.user import User, UserStatus
from modules.user_management.domain.ports.password_service_protocol import (
    PasswordServiceProtocol,
)
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)


class AuthenticationService:
    """Domain service for user authentication business logic."""

    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        password_service: PasswordServiceProtocol,
        max_login_attempts: int = 5,
        token_expiry_hours: int = 24,
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._max_login_attempts = max_login_attempts
        self._token_expiry_hours = token_expiry_hours

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Register a new user account."""
        # Check if user already exists
        existing_user = await self._user_repository.get_by_email(email)
        if existing_user is not None:
            raise ValueError("User with this email already exists")

        # Validate password strength
        if not self._is_password_strong(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, number and special character"
            )

        # Hash password
        password_hash = await self._password_service.hash_password(password)

        # Generate email verification token
        email_verification_token = self._generate_secure_token()

        # Create user entity
        user = User(
            id=uuid4(),
            email=email.lower().strip(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            status=UserStatus.PENDING_VERIFICATION,
            is_active=True,
            is_email_verified=False,
            email_verification_token=email_verification_token,
            created_at=datetime.now(UTC),
        )

        # Save user
        saved_user = await self._user_repository.create(user)

        # TODO: Send verification email via notification service

        return saved_user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user credentials."""
        user = await self._user_repository.get_by_email(email.lower().strip())

        if user is None:
            return None

        # Check if account is locked
        if user.is_account_locked(self._max_login_attempts):
            raise ValueError(
                f"Account locked due to {self._max_login_attempts} failed login attempts"
            )

        # Check if account is active
        if not user.is_active or user.status == UserStatus.SUSPENDED:
            raise ValueError("Account is not active")

        # Verify password
        password_valid = await self._password_service.verify_password(
            password, user.password_hash
        )

        if not password_valid:
            user.record_failed_login()
            await self._user_repository.update(user)
            return None

        # Successful authentication
        user.record_login()
        await self._user_repository.update(user)

        return user

    async def verify_email(self, user_id: UUID, verification_token: str) -> bool:
        """Verify user's email address using verification token."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return False

        if user.email_verification_token != verification_token:
            return False

        if user.is_email_verified:
            return True  # Already verified

        user.verify_email()
        await self._user_repository.update(user)

        return True

    async def initiate_password_reset(self, email: str) -> str | None:
        """Initiate password reset process for user."""
        user = await self._user_repository.get_by_email(email.lower().strip())

        if user is None:
            # Don't reveal whether user exists
            return None

        # Generate password reset token
        reset_token = self._generate_secure_token()
        user.password_reset_token = reset_token
        user.password_reset_expires_at = datetime.now(UTC) + timedelta(
            hours=self._token_expiry_hours
        )

        await self._user_repository.update(user)

        # TODO: Send password reset email via notification service

        return reset_token

    async def reset_password(
        self, user_id: UUID, reset_token: str, new_password: str
    ) -> bool:
        """Reset user password using reset token."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return False

        if (
            user.password_reset_token != reset_token
            or user.password_reset_expires_at is None
            or user.password_reset_expires_at < datetime.now(UTC)
        ):
            return False

        # Validate new password
        if not self._is_password_strong(new_password):
            raise ValueError(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, number and special character"
            )

        # Hash new password
        user.password_hash = await self._password_service.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires_at = None
        user.reset_failed_logins()

        await self._user_repository.update(user)

        return True

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> bool:
        """Change user password with current password verification."""
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            return False

        # Verify current password
        password_valid = await self._password_service.verify_password(
            current_password, user.password_hash
        )

        if not password_valid:
            return False

        # Validate new password
        if not self._is_password_strong(new_password):
            raise ValueError(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, number and special character"
            )

        # Hash new password
        user.password_hash = await self._password_service.hash_password(new_password)

        await self._user_repository.update(user)

        return True

    def _is_password_strong(self, password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return has_upper and has_lower and has_digit and has_special

    def _generate_secure_token(self) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
