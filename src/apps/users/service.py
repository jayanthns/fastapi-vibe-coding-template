"""
User service with business logic for user management.
"""

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.repository import UserRepository
from src.apps.users.schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserPasswordChange,
    UserResponse,
    UserUpdate,
)
from src.utils.security import create_access_token, create_refresh_token


class UserService:
    """Service for user management operations."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_create: UserCreate) -> Tuple[UserResponse, str]:
        """
        Create a new user and return user data with access token.

        Args:
            user_create: User creation data

        Returns:
            Tuple of (user_data, access_token)

        Raises:
            ValueError: If email or username already exists
        """
        # Check if email already exists
        existing_user = await self.repository.get_by_email(user_create.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Check if username already exists
        existing_username = await self.repository.get_by_username(user_create.username)
        if existing_username:
            raise ValueError("Username already taken")

        # Create user (password will be hashed in the repository)
        user = await self.repository.create(user_create)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return UserResponse.model_validate(user), access_token

    async def authenticate_user(
        self, user_login: UserLogin
    ) -> Tuple[UserResponse, str]:
        """
        Authenticate a user and return user data with access token.

        Args:
            user_login: User login credentials

        Returns:
            Tuple of (user_data, access_token)

        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email or username
        user = await self.repository.get_by_email_or_username(user_login.email)
        if not user:
            raise ValueError("Invalid credentials")

        # Verify password using the model method
        if not user.verify_password(user_login.password):
            raise ValueError("Invalid credentials")

        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is deactivated")

        # Update last login
        await self.repository.update_last_login(user.id)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return UserResponse.model_validate(user), access_token

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserResponse]:
        """Get user by ID."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def update_user(
        self, user_id: UUID, user_update: UserUpdate
    ) -> Optional[UserResponse]:
        """Update user profile."""
        user = await self.repository.update(user_id, user_update)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def change_password(
        self, user_id: UUID, password_change: UserPasswordChange
    ) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            password_change: Password change data

        Returns:
            True if successful, False if user not found

        Raises:
            ValueError: If current password is incorrect
        """
        # Get user
        user = await self.repository.get_by_id(user_id)
        if not user:
            return False

        # Verify current password using the model method
        if not user.verify_password(password_change.current_password):
            raise ValueError("Current password is incorrect")

        # Update password (will be hashed in the repository)
        updated_user = await self.repository.update_password(
            user_id, password_change.new_password
        )
        return updated_user is not None

    async def verify_user(self, user_id: UUID) -> Optional[UserResponse]:
        """Verify a user account."""
        user = await self.repository.verify_user(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def deactivate_user(self, user_id: UUID) -> Optional[UserResponse]:
        """Deactivate a user account."""
        user = await self.repository.deactivate_user(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def activate_user(self, user_id: UUID) -> Optional[UserResponse]:
        """Activate a user account."""
        user = await self.repository.activate_user(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def make_superuser(self, user_id: UUID) -> Optional[UserResponse]:
        """Make a user a superuser."""
        user = await self.repository.make_superuser(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[list[UserResponse], int]:
        """Get list of users with pagination."""
        users, total = await self.repository.get_all(
            skip=skip, limit=limit, search=search, is_active=is_active
        )
        user_responses = [UserResponse.model_validate(user) for user in users]
        return user_responses, total

    async def create_token_pair(self, user_id: UUID, email: str) -> Tuple[str, str]:
        """
        Create both access and refresh tokens for a user.

        Args:
            user_id: User ID
            email: User email

        Returns:
            Tuple of (access_token, refresh_token)
        """
        token_data = {"sub": str(user_id), "email": email}

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create a new access token using a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token or None if refresh token is invalid
        """
        from src.utils.security import verify_token

        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            return None

        # Verify user still exists and is active
        user = await self.repository.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            return None

        # Create new access token
        return create_access_token(data={"sub": user_id, "email": email})
