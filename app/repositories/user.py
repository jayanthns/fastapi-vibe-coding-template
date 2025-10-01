"""
Repository for user management operations.
"""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """Repository for user management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_create: UserCreate) -> User:
        """Create a new user."""
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            age=user_create.age,
        )
        # Set password using the secure method
        db_user.set_password(user_create.password)

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get a user by email or username."""
        result = await self.db.execute(
            select(User).where(
                or_(User.email == identifier, User.username == identifier)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        """Get all users with pagination and filtering."""
        query = select(User)
        count_query = select(func.count(User.id))

        # Apply filters
        filters = []
        if search:
            filters.append(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                )
            )
        if is_active is not None:
            filters.append(User.is_active == is_active)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        result = await self.db.execute(
            query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        items = list(result.scalars().all())

        return items, total

    async def update(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update a user."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update_password(self, user_id: UUID, new_password: str) -> Optional[User]:
        """Update user password."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        # Set password using the secure method
        db_user.set_password(new_password)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update_last_login(self, user_id: UUID) -> Optional[User]:
        """Update user's last login time."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.last_login = func.now()  # type: ignore
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def verify_user(self, user_id: UUID) -> Optional[User]:
        """Mark user as verified."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_verified = True  # type: ignore
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate a user."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_active = False  # type: ignore
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activate a user."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_active = True  # type: ignore
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user (soft delete by deactivating)."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False

        # Soft delete by deactivating
        db_user.is_active = False  # type: ignore
        await self.db.commit()
        return True

    async def make_superuser(self, user_id: UUID) -> Optional[User]:
        """Make a user a superuser."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_superuser = True  # type: ignore
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
