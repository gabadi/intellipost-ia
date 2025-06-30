"""
Concrete implementation of authentication service.

This module provides the main authentication service implementation.
"""

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.domain.models import AuthenticatedUser, AuthResult, TokenPair
from modules.auth.infrastructure.jwt_manager import JWTManager
from modules.auth.infrastructure.password_manager import PasswordManager
from modules.auth.infrastructure.token_blacklist import token_blacklist
from modules.user.domain.user_status import UserStatus
from modules.user.infrastructure.models import RefreshTokenModel, UserModel


class AuthenticationServiceImpl:
    """Implementation of authentication service."""

    def __init__(self, db_session: AsyncSession):
        """Initialize service with database session."""
        self.db_session = db_session
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager()

    async def register_user(self, email: str, password: str) -> AuthResult:
        """Register a new user and return authentication tokens."""
        # Validate email format
        if not self._validate_email(email):
            raise ValueError("Invalid email format")

        # Validate password strength
        is_valid, error_msg = self.password_manager.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error_msg)

        # Check if user already exists
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.db_session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Create new user
        user_model = UserModel(
            email=email,
            password_hash=self.password_manager.hash_password(password),
            status=UserStatus.PENDING_VERIFICATION.value,
            is_active=True,
            failed_login_attempts=0,
        )

        self.db_session.add(user_model)
        await self.db_session.commit()
        await self.db_session.refresh(user_model)

        # Generate tokens
        access_token = self.jwt_manager.create_access_token(
            user_model.id, user_model.email
        )
        refresh_token, expires_at = self.jwt_manager.create_refresh_token(user_model.id)

        # Store refresh token
        await self._store_refresh_token(user_model.id, refresh_token, expires_at)

        # Track refresh token for bulk revocation
        await token_blacklist.track_user_token(
            str(user_model.id), refresh_token, "refresh"
        )

        return AuthResult(
            user_id=user_model.id,
            email=user_model.email,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def authenticate_user(self, email: str, password: str) -> AuthResult:
        """Authenticate user credentials and return tokens."""
        # Get user
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.db_session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            raise ValueError("Authentication failed")

        # Check if account is locked
        if await self._is_account_locked(user_model):
            raise ValueError(
                "Account temporarily locked due to multiple failed login attempts"
            )

        # Verify password
        if not self.password_manager.verify_password(
            password, user_model.password_hash
        ):
            await self._record_failed_login(user_model)
            raise ValueError("Authentication failed")

        # Check if user is active
        if not user_model.is_active:
            raise ValueError("Authentication failed")

        # Reset failed login attempts and update last login
        user_model.failed_login_attempts = 0
        user_model.last_failed_login_at = None
        user_model.last_login_at = datetime.now(UTC)

        # Generate tokens
        access_token = self.jwt_manager.create_access_token(
            user_model.id, user_model.email
        )
        refresh_token, expires_at = self.jwt_manager.create_refresh_token(user_model.id)

        # Store refresh token
        await self._store_refresh_token(user_model.id, refresh_token, expires_at)

        # Track refresh token for bulk revocation
        await token_blacklist.track_user_token(
            str(user_model.id), refresh_token, "refresh"
        )

        await self.db_session.commit()

        return AuthResult(
            user_id=user_model.id,
            email=user_model.email,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def validate_token(self, access_token: str) -> AuthenticatedUser:
        """Validate an access token and return user information."""
        try:
            payload = await self.jwt_manager.validate_access_token(access_token)
            user_id = UUID(payload["sub"])
            email = payload["email"]

            # Verify user still exists and is active
            stmt = select(UserModel).where(UserModel.id == user_id, UserModel.is_active)
            result = await self.db_session.execute(stmt)
            if not result.scalar_one_or_none():
                raise ValueError("Authentication required")

            return AuthenticatedUser(user_id=user_id, email=email)
        except (JWTError, KeyError, ValueError) as e:
            raise ValueError("Authentication required") from e

    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh authentication tokens using a refresh token."""
        try:
            # Validate refresh token
            payload = await self.jwt_manager.validate_refresh_token(refresh_token)
            user_id = UUID(payload["sub"])

            # Verify refresh token exists in database
            token_hash = self._hash_token(refresh_token)
            stmt = select(RefreshTokenModel).where(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.expires_at > datetime.now(UTC),
            )
            result = await self.db_session.execute(stmt)
            stored_token = result.scalar_one_or_none()

            if not stored_token:
                raise ValueError("Token refresh failed")

            # Get user
            stmt = select(UserModel).where(UserModel.id == user_id, UserModel.is_active)
            result = await self.db_session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if not user_model:
                raise ValueError("Token refresh failed")

            # Delete old refresh token
            await self.db_session.delete(stored_token)

            # Generate new tokens
            access_token = self.jwt_manager.create_access_token(
                user_model.id, user_model.email
            )
            new_refresh_token, expires_at = self.jwt_manager.create_refresh_token(
                user_model.id
            )

            # Store new refresh token
            await self._store_refresh_token(
                user_model.id, new_refresh_token, expires_at
            )

            # Track new refresh token for bulk revocation
            await token_blacklist.track_user_token(
                str(user_model.id), new_refresh_token, "refresh"
            )

            # Remove old refresh token from tracking
            await token_blacklist.remove_user_token(
                str(user_model.id), refresh_token, "refresh"
            )

            await self.db_session.commit()

            return TokenPair(access_token=access_token, refresh_token=new_refresh_token)
        except (JWTError, ValueError) as e:
            raise ValueError("Token refresh failed") from e

    async def logout_user(self, user_id: UUID) -> None:
        """Logout user by invalidating their refresh tokens."""
        # Blacklist all user tokens in Redis
        await token_blacklist.blacklist_all_user_tokens(str(user_id))

        # Delete refresh tokens from database
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> None:
        """
        Change user password and invalidate all sessions.

        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password to set

        Raises:
            ValueError: If current password is incorrect or new password is invalid
        """
        # Get user
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.db_session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            raise ValueError("User not found")

        # Verify current password
        if not self.password_manager.verify_password(
            current_password, user_model.password_hash
        ):
            raise ValueError("Current password is incorrect")

        # Validate new password strength
        is_valid, error_msg = self.password_manager.validate_password_strength(
            new_password
        )
        if not is_valid:
            raise ValueError(error_msg)

        # Update password
        user_model.password_hash = self.password_manager.hash_password(new_password)
        user_model.password_changed_at = datetime.now(UTC)

        # Invalidate all sessions for security
        await self.logout_user(user_id)

        await self.db_session.commit()

    # Helper methods

    def _validate_email(self, email: str) -> bool:
        """Basic email validation."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _hash_token(self, token: str) -> str:
        """Hash a token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def _store_refresh_token(
        self, user_id: UUID, token: str, expires_at: datetime
    ) -> None:
        """Store a refresh token in the database."""
        token_model = RefreshTokenModel(
            user_id=user_id, token_hash=self._hash_token(token), expires_at=expires_at
        )
        self.db_session.add(token_model)

    async def _is_account_locked(self, user_model: UserModel) -> bool:
        """Check if account is locked due to failed login attempts."""
        if user_model.failed_login_attempts >= 5:
            if user_model.last_failed_login_at:
                lockout_duration = timedelta(minutes=15)
                if (
                    datetime.now(UTC) - user_model.last_failed_login_at
                    < lockout_duration
                ):
                    return True
                else:
                    # Reset failed attempts after lockout period
                    user_model.failed_login_attempts = 0
                    user_model.last_failed_login_at = None
        return False

    async def _record_failed_login(self, user_model: UserModel) -> None:
        """Record a failed login attempt."""
        user_model.failed_login_attempts += 1
        user_model.last_failed_login_at = datetime.now(UTC)
        await self.db_session.commit()
