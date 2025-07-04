"""
Enhanced Authentication service for user management.

This module contains an enhanced authentication service that naturally satisfies
the API AuthenticationProviderProtocol through duck typing. It implements all
required methods with compatible signatures, eliminating the need for adapter classes.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from modules.user_management.domain.entities.refresh_token import RefreshToken
from modules.user_management.domain.entities.user import User, UserStatus
from modules.user_management.domain.exceptions import (
    AccountInactiveError,
    AccountLockedError,
    UserAlreadyExistsError,
    WeakPasswordError,
)
from modules.user_management.domain.ports.jwt_service_protocol import (
    JWTServiceProtocol,
)
from modules.user_management.domain.ports.password_service_protocol import (
    PasswordServiceProtocol,
)
from modules.user_management.domain.ports.refresh_token_repository_protocol import (
    RefreshTokenRepositoryProtocol,
)
from modules.user_management.domain.ports.user_repository_protocol import (
    UserRepositoryProtocol,
)


# API Protocol compatibility types
# These are lightweight types that match the API protocol signatures
class AuthenticationCredentials:
    """Credentials for authentication."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password


class UserRegistrationData:
    """User registration data."""

    def __init__(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name


class AuthenticatedUser:
    """Authenticated user data for API responses."""

    def __init__(
        self,
        id: UUID,
        email: str,
        first_name: str | None,
        last_name: str | None,
        is_active: bool,
        created_at: str,
        last_login_at: str | None,
    ):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.created_at = created_at
        self.last_login_at = last_login_at


class TokenPair:
    """JWT token pair."""

    def __init__(
        self, access_token: str, refresh_token: str, token_type: str = "bearer"
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type


class AuthenticationResult:
    """Result of authentication operations."""

    def __init__(self, user: AuthenticatedUser, tokens: TokenPair):
        self.user = user
        self.tokens = tokens


class EnhancedAuthenticationService:
    """
    Enhanced authentication service that naturally satisfies the API protocol.

    This service implements all methods required by the AuthenticationProviderProtocol
    through duck typing, eliminating the need for adapter classes. It combines
    domain business logic with API-compatible method signatures.
    """

    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        password_service: PasswordServiceProtocol,
        jwt_service: JWTServiceProtocol,
        refresh_token_repository: RefreshTokenRepositoryProtocol,
        max_login_attempts: int = 5,
        token_expiry_hours: int = 24,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._jwt_service = jwt_service
        self._refresh_token_repository = refresh_token_repository
        self._max_login_attempts = max_login_attempts
        self._token_expiry_hours = token_expiry_hours
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    # API Protocol Methods - These naturally satisfy the AuthenticationProviderProtocol

    async def authenticate_user(
        self, credentials: AuthenticationCredentials
    ) -> AuthenticationResult | None:
        """
        Authenticate a user with email and password.

        This method signature matches the API protocol exactly,
        allowing duck typing to work seamlessly.
        """
        user = await self._authenticate_user_domain(
            credentials.email, credentials.password
        )

        if user is None:
            return None

        tokens = await self._generate_tokens_for_user(user)

        return AuthenticationResult(
            user=self._user_to_authenticated_user(user), tokens=tokens
        )

    async def register_user(
        self, registration_data: UserRegistrationData
    ) -> AuthenticationResult:
        """
        Register a new user.

        This method signature matches the API protocol exactly.
        """
        user = await self._register_user_domain(
            registration_data.email,
            registration_data.password,
            registration_data.first_name,
            registration_data.last_name,
        )

        tokens = await self._generate_tokens_for_user(user)

        return AuthenticationResult(
            user=self._user_to_authenticated_user(user), tokens=tokens
        )

    async def refresh_tokens(self, refresh_token: str) -> AuthenticationResult | None:
        """
        Refresh access token using refresh token.

        This method signature matches the API protocol exactly.
        """
        result = await self._refresh_tokens_domain(refresh_token)

        if result is None:
            return None

        user, tokens = result

        return AuthenticationResult(
            user=self._user_to_authenticated_user(user), tokens=tokens
        )

    async def logout_user(self, access_token: str) -> bool:
        """
        Logout user and invalidate tokens.

        This method signature matches the API protocol exactly.
        """
        return await self._logout_user_domain(access_token)

    async def get_current_user(self, access_token: str) -> AuthenticatedUser | None:
        """
        Get current user from access token.

        This method signature matches the API protocol exactly.
        """
        user = await self._get_current_user_domain(access_token)

        if user is None:
            return None

        return self._user_to_authenticated_user(user)

    # Domain Business Logic Methods - Private methods that implement the actual business logic

    async def _authenticate_user_domain(self, email: str, password: str) -> User | None:
        """Domain logic for user authentication."""
        user = await self._user_repository.get_by_email(email.lower().strip())

        if user is None:
            return None

        # Check if account is locked
        if user.is_account_locked(self._max_login_attempts):
            raise AccountLockedError(
                user.failed_login_attempts, self._max_login_attempts
            )

        # Check if account is active
        if not user.is_active or user.status == UserStatus.SUSPENDED:
            raise AccountInactiveError()

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

    async def _register_user_domain(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Domain logic for user registration."""
        # Check if user already exists
        existing_user = await self._user_repository.get_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError(email)

        # Validate password strength
        if not self._is_password_strong(password):
            raise WeakPasswordError()

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

    async def _refresh_tokens_domain(
        self, refresh_token: str
    ) -> tuple[User, TokenPair] | None:
        """Domain logic for token refresh."""
        try:
            # Verify refresh token
            payload = self._jwt_service.verify_token(refresh_token)
            if payload is None:
                return None

            # Check token type
            token_type = payload.get("type")
            if token_type != "refresh":
                return None

            # Extract user ID
            user_id = self._jwt_service.extract_user_id(refresh_token)
            if user_id is None:
                return None

            # Get user
            user = await self._user_repository.get_by_id(user_id)
            if user is None:
                return None

            # Check if user is active
            if not user.is_active:
                return None

            # Check if refresh token exists in database
            refresh_token_hash = self._hash_token(refresh_token)
            stored_token = await self._refresh_token_repository.get_by_token_hash(
                refresh_token_hash
            )

            if stored_token is None or stored_token.is_expired():
                return None

            # Generate new tokens
            tokens = await self._generate_tokens_for_user(user)

            # Remove old refresh token
            await self._refresh_token_repository.delete_by_token_hash(
                refresh_token_hash
            )

            return user, tokens

        except Exception:
            return None

    async def _logout_user_domain(self, access_token: str) -> bool:
        """Domain logic for user logout."""
        try:
            # Verify access token
            payload = self._jwt_service.verify_token(access_token)
            if payload is None:
                return False

            # Extract user ID
            user_id = self._jwt_service.extract_user_id(access_token)
            if user_id is None:
                return False

            # Delete all refresh tokens for this user
            await self._refresh_token_repository.delete_by_user_id(user_id)

            return True

        except Exception:
            return False

    async def _get_current_user_domain(self, access_token: str) -> User | None:
        """Domain logic for getting current user from token."""
        try:
            # Verify token
            payload = self._jwt_service.verify_token(access_token)
            if payload is None:
                return None

            # Check token type
            token_type = payload.get("type")
            if token_type != "access":
                return None

            # Extract user ID
            user_id = self._jwt_service.extract_user_id(access_token)
            if user_id is None:
                return None

            # Get user
            user = await self._user_repository.get_by_id(user_id)
            if user is None:
                return None

            # Check if user is active
            if not user.is_active:
                return None

            return user

        except Exception:
            return None

    async def _generate_tokens_for_user(self, user: User) -> TokenPair:
        """Generate JWT tokens for a user."""
        # Create access token
        access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            expires_delta=timedelta(minutes=self._access_token_expire_minutes),
        )

        # Create refresh token
        refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
            expires_delta=timedelta(days=self._refresh_token_expire_days),
        )

        # Store refresh token hash in database
        refresh_token_hash = self._hash_token(refresh_token)
        refresh_token_entity = RefreshToken(
            id=uuid4(),
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.now(UTC)
            + timedelta(days=self._refresh_token_expire_days),
            created_at=datetime.now(UTC),
        )

        await self._refresh_token_repository.create(refresh_token_entity)

        return TokenPair(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    def _user_to_authenticated_user(self, user: User) -> AuthenticatedUser:
        """Convert internal User entity to API AuthenticatedUser."""
        return AuthenticatedUser(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login_at=user.last_login_at.isoformat()
            if user.last_login_at
            else None,
        )

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

    def _hash_token(self, token: str) -> str:
        """Hash a refresh token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    # Legacy domain methods for backwards compatibility
    # These maintain compatibility with existing code that uses the original AuthenticationService

    async def authenticate_user_legacy(self, email: str, password: str) -> User | None:
        """Legacy method for backwards compatibility."""
        return await self._authenticate_user_domain(email, password)

    async def register_user_legacy(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Legacy method for backwards compatibility."""
        return await self._register_user_domain(email, password, first_name, last_name)

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
            raise WeakPasswordError()

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
            raise WeakPasswordError()

        # Hash new password
        user.password_hash = await self._password_service.hash_password(new_password)

        await self._user_repository.update(user)

        return True
