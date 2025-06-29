"""
Authentication service implementation.

This module provides the concrete implementation of the AuthenticationService
protocol, coordinating between user repository, password service, and JWT service.
"""

import re
from datetime import UTC, datetime
from uuid import uuid4

from jose import JWTError

from modules.auth.domain.models import (
    AuthenticatedUser,
    AuthResult,
)
from modules.auth.infrastructure.jwt_service import JWTService
from modules.auth.infrastructure.password_service import PasswordService
from modules.user.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
)
from modules.user.domain.ports.user_repository_protocol import UserRepositoryProtocol
from modules.user.domain.user import User
from modules.user.domain.user_status import UserStatus


class AuthenticationService:
    """
    Authentication service implementation.

    Coordinates user registration, authentication, and token management
    using the injected dependencies.
    """

    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        password_service: PasswordService,
        jwt_service: JWTService,
    ) -> None:
        """
        Initialize authentication service with dependencies.

        Args:
            user_repository: Repository for user data operations
            password_service: Service for password hashing and verification
            jwt_service: Service for JWT token operations
        """
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> AuthResult:
        """
        Register a new user account.

        Args:
            email: User's email address
            password: Plain text password
            first_name: User's first name (optional)
            last_name: User's last name (optional)

        Returns:
            AuthResult: Registration result with user and tokens
        """
        try:
            # Validate input
            self._validate_email(email)
            self._validate_password(password)

            # Check if user already exists
            if await self.user_repository.email_exists(email):
                return AuthResult.failure_result("User with this email already exists")

            # Hash password
            password_hash = self.password_service.hash_password(password)

            # Create user entity
            user = User(
                id=uuid4(),
                email=email.lower().strip(),
                password_hash=password_hash,
                first_name=first_name.strip() if first_name else None,
                last_name=last_name.strip() if last_name else None,
                status=UserStatus.ACTIVE,  # Auto-activate for MVP
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            # Save user to repository
            created_user = await self.user_repository.create(user)

            # Generate JWT tokens
            token_pair = self.jwt_service.create_token_pair(
                user_id=created_user.id,
                email=created_user.email,
                is_active=created_user.is_active,
            )

            return AuthResult.success_result(
                user=created_user,
                access_token=token_pair.access_token,
                refresh_token=token_pair.refresh_token,
                expires_in=token_pair.expires_in,
            )

        except UserAlreadyExistsError:
            return AuthResult.failure_result("User with this email already exists")
        except ValueError as e:
            return AuthResult.failure_result(str(e))
        except Exception as e:
            return AuthResult.failure_result(f"Registration failed: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> AuthResult:
        """
        Authenticate user with email and password.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            AuthResult: Authentication result with user and tokens
        """
        try:
            # Validate input
            if not email or not password:
                return AuthResult.failure_result("Email and password are required")

            # Get user by email
            user = await self.user_repository.get_by_email(email.lower().strip())
            if not user:
                return AuthResult.failure_result("Invalid email or password")

            # Verify password
            if not self.password_service.verify_password(password, user.password_hash):
                return AuthResult.failure_result("Invalid email or password")

            # Check if user is active
            if not user.is_active:
                return AuthResult.failure_result("Account is not active")

            # Update last login
            await self.user_repository.update_last_login(user.id)

            # Generate JWT tokens
            token_pair = self.jwt_service.create_token_pair(
                user_id=user.id,
                email=user.email,
                is_active=user.is_active,
            )

            return AuthResult.success_result(
                user=user,
                access_token=token_pair.access_token,
                refresh_token=token_pair.refresh_token,
                expires_in=token_pair.expires_in,
            )

        except UserNotFoundError:
            return AuthResult.failure_result("Invalid email or password")
        except UserNotActiveError:
            return AuthResult.failure_result("Account is not active")
        except InvalidCredentialsError:
            return AuthResult.failure_result("Invalid email or password")
        except Exception as e:
            return AuthResult.failure_result(f"Authentication failed: {str(e)}")

    async def validate_token(self, access_token: str) -> AuthenticatedUser:
        """
        Validate an access token and return user information.

        Args:
            access_token: JWT access token

        Returns:
            AuthenticatedUser: User information from token

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            # Validate token with JWT service
            auth_user = self.jwt_service.validate_access_token(access_token)

            # Verify user still exists and is active
            user = await self.user_repository.get_by_id(auth_user.user_id)
            if not user or not user.is_active:
                raise JWTError("User is no longer active")

            return AuthenticatedUser(
                user_id=auth_user.user_id,
                email=auth_user.email,
                is_active=auth_user.is_active,
                exp=auth_user.exp,
            )

        except JWTError:
            raise
        except Exception as e:
            raise JWTError(f"Token validation failed: {str(e)}")

    async def refresh_token(self, refresh_token: str) -> str:
        """
        Create a new access token from a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            str: New access token

        Raises:
            JWTError: If refresh token is invalid or expired
        """
        try:
            # Validate refresh token and get user info
            auth_user = self.jwt_service.validate_refresh_token(refresh_token)

            # Verify user still exists and is active
            user = await self.user_repository.get_by_id(auth_user.user_id)
            if not user or not user.is_active:
                raise JWTError("User is no longer active")

            # Create new access token
            return self.jwt_service.create_access_token_from_refresh(refresh_token)

        except JWTError:
            raise
        except Exception as e:
            raise JWTError(f"Token refresh failed: {str(e)}")

    async def logout_user(self, refresh_token: str) -> bool:
        """
        Logout user by validating refresh token.

        Note: In this MVP implementation, we don't maintain a token blacklist,
        so this method validates the token but doesn't actually invalidate it.

        Args:
            refresh_token: Refresh token to validate

        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            # Validate refresh token
            self.jwt_service.validate_refresh_token(refresh_token)
            return True
        except JWTError:
            return False

    def _validate_email(self, email: str) -> None:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Raises:
            ValueError: If email format is invalid
        """
        if not email:
            raise ValueError("Email is required")

        email = email.strip()
        if len(email) < 5 or len(email) > 255:
            raise ValueError("Email must be between 5 and 255 characters")

        # Basic email format validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

    def _validate_password(self, password: str) -> None:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not password:
            raise ValueError("Password is required")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(password) > 128:
            raise ValueError("Password must not exceed 128 characters")

        # Check for mixed case and numbers
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one number"
            )
