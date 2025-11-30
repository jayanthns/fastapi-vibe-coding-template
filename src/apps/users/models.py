"""
User model with industry-standard fields and UUID primary key.
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import UUIDModel
from src.db.session import Base


class User(Base, UUIDModel):
    """User model with comprehensive fields for user management."""

    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    _password_hash = Column("password_hash", String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

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
