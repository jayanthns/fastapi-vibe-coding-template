"""
Common enums used across the application.
"""

from enum import Enum


class StrEnum(str, Enum):
    """Base class for string enums."""

    def __str__(self) -> str:
        return self.value


class AuditAction(StrEnum):
    """Audit action types for tracking user activities."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    OTHER = "OTHER"
