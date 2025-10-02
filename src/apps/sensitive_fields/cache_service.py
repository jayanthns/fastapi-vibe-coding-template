"""
Service for caching and retrieving sensitive field patterns.
"""

import asyncio
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.apps.sensitive_fields.repository import SensitiveFieldRepository


class SensitiveFieldCacheService:
    """Service for caching sensitive field patterns."""

    _cache: Optional[List[Dict[str, Any]]] = None
    _cache_lock = asyncio.Lock()

    @classmethod
    async def get_sensitive_patterns(
        cls, db: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sensitive field patterns, using cache if available.

        Args:
            db: Database session (optional, will create new if not provided)

        Returns:
            List of sensitive field patterns
        """
        # If cache is available, return it
        if cls._cache is not None:
            return cls._cache

        # If no database session provided, create one
        if db is None:
            async for session in get_db():
                return await cls._load_patterns_from_db(session)
            # This should never be reached, but added for completeness
            raise RuntimeError("Failed to get database session")
        else:
            return await cls._load_patterns_from_db(db)

    @classmethod
    async def _load_patterns_from_db(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        """Load patterns from database and cache them."""
        async with cls._cache_lock:
            # Double-check cache after acquiring lock
            if cls._cache is not None:
                return cls._cache

            repository = SensitiveFieldRepository(db)
            patterns = await repository.get_all_active()

            # Convert to dict format
            cls._cache = [
                {
                    "field_name": pattern.field_name,
                    "is_exact_match": pattern.is_exact_match,
                    "description": pattern.description,
                }
                for pattern in patterns
            ]

            return cls._cache

    @classmethod
    def invalidate_cache(cls):
        """Invalidate the cache to force reload on next access."""
        cls._cache = None

    @classmethod
    def get_cached_patterns(cls) -> Optional[List[Dict[str, Any]]]:
        """Get cached patterns without database access."""
        return cls._cache
