"""
Common enums used across the application.
"""

from enum import Enum


class AuditAction(str, Enum):
    """Audit action types for tracking user activities."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    OTHER = "OTHER"

    def __str__(self) -> str:
        return self.value
