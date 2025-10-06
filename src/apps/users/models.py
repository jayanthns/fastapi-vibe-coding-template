"""
User model with industry-standard fields and comprehensive user management.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.apps.base_models import BaseModel


class User(BaseModel):
    """
    User model with comprehensive fields for user management.

    Extends BaseModel to inherit:
    - UUID primary key (id)
    - Created and updated timestamps (created_at, updated_at)
    - Automatic table naming (users)
    - Common utility methods
    """

    # User authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="User's email address",
    )
    username: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True, comment="Unique username"
    )
    _password_hash: Mapped[str] = mapped_column(
        "password_hash", String(255), nullable=False, comment="Hashed password"
    )

    # User profile fields
    first_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="User's first name"
    )
    last_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="User's last name"
    )
    age: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="User's age"
    )

    # User status fields
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user's email is verified",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user has superuser privileges",
    )

    # Activity tracking
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="When the user last logged in"
    )

    def __repr__(self):
        return (
            f"<User(id={self.id}, username='{self.username}', "
            f"email='{self.email}', is_active={self.is_active})>"
        )

    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def set_password(self, password: str) -> None:
        """
        Set the user's password (will be hashed automatically).

        Args:
            password: Plain text password to hash and store
        """
        from src.utils.security import get_password_hash

        self._password_hash = get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        from src.utils.security import verify_password

        return verify_password(password, self._password_hash)

    @property
    def password_hash(self) -> str:
        """
        Get the password hash (for internal use only).

        Returns:
            The hashed password string

        Note:
            This should only be used for database operations and testing.
            Never expose this in API responses.
        """
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value: str) -> None:
        """
        Set the password hash directly (for internal use only).

        Args:
            value: Pre-hashed password string

        Note:
            This should only be used for database operations and testing.
            Use set_password() for setting plain text passwords.
        """
        self._password_hash = value
