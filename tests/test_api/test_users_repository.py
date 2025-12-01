from uuid import uuid4

import pytest

from src.apps.users.repository import UserRepository
from src.apps.users.schemas import UserCreate, UserUpdate


@pytest.mark.asyncio
class TestUserRepository:
    async def test_create_user(self, async_session):
        repo = UserRepository(async_session)
        user_create = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="Password123!",
            age=25,
        )
        user = await repo.create(user_create)
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.verify_password("Password123!") is True

    async def test_get_by_id(self, async_session):
        repo = UserRepository(async_session)
        user_create = UserCreate(
            email="test2@example.com",
            username="testuser2",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )
        created_user = await repo.create(user_create)

        fetched_user = await repo.get_by_id(created_user.id)
        assert fetched_user is not None
        assert fetched_user.id == created_user.id

    async def test_get_by_email(self, async_session):
        repo = UserRepository(async_session)
        user_create = UserCreate(
            email="test3@example.com",
            username="testuser3",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )
        await repo.create(user_create)

        fetched_user = await repo.get_by_email("test3@example.com")
        assert fetched_user is not None
        assert fetched_user.email == "test3@example.com"

    async def test_update_user(self, async_session):
        repo = UserRepository(async_session)
        user_create = UserCreate(
            email="test4@example.com",
            username="testuser4",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )
        user = await repo.create(user_create)

        update_data = UserUpdate(first_name="Updated", age=30)
        updated_user = await repo.update(user.id, update_data)

        assert updated_user.first_name == "Updated"
        assert updated_user.age == 30
        assert updated_user.email == "test4@example.com"

    async def test_delete_user(self, async_session):
        repo = UserRepository(async_session)
        user_create = UserCreate(
            email="test5@example.com",
            username="testuser5",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )
        user = await repo.create(user_create)

        result = await repo.delete(user.id)
        assert result is True

        fetched_user = await repo.get_by_id(user.id)
        assert fetched_user.is_active is False

    async def test_get_all_users(self, async_session):
        repo = UserRepository(async_session)
        # Create multiple users
        for i in range(3):
            await repo.create(
                UserCreate(
                    email=f"list{i}@example.com",
                    username=f"listuser{i}",
                    first_name="Test",
                    last_name="User",
                    password="Password123!",
                )
            )

        users, total = await repo.get_all(limit=10)
        # Note: other tests might have created users too, so check >= 3
        assert len(users) >= 3
        assert total >= 3

    async def test_get_by_username(self, async_session):
        repo = UserRepository(async_session)
        user_create = UserCreate(
            email="username_test@example.com",
            username="unique_username",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )
        await repo.create(user_create)

        user = await repo.get_by_username("unique_username")
        assert user is not None
        assert user.email == "username_test@example.com"

    async def test_get_by_email_or_username(self, async_session):
        repo = UserRepository(async_session)
        user_create = UserCreate(
            email="identifier_test@example.com",
            username="identifier_user",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )
        await repo.create(user_create)

        # Test by email
        user1 = await repo.get_by_email_or_username("identifier_test@example.com")
        assert user1 is not None
        assert user1.username == "identifier_user"

        # Test by username
        user2 = await repo.get_by_email_or_username("identifier_user")
        assert user2 is not None
        assert user2.email == "identifier_test@example.com"

    async def test_get_all_with_filters(self, async_session):
        repo = UserRepository(async_session)
        await repo.create(
            UserCreate(
                email="search_match@example.com",
                username="search_match",
                first_name="Search",
                last_name="Match",
                password="Password123!",
            )
        )

        # Test search
        users, total = await repo.get_all(search="Search")
        assert len(users) >= 1
        assert any(u.email == "search_match@example.com" for u in users)

        # Test is_active filter
        users_active, _ = await repo.get_all(is_active=True)
        assert all(u.is_active for u in users_active)

    async def test_update_not_found(self, async_session):
        repo = UserRepository(async_session)
        result = await repo.update(uuid4(), UserUpdate(first_name="Ghost"))
        assert result is None

    async def test_update_password(self, async_session):
        repo = UserRepository(async_session)
        user = await repo.create(
            UserCreate(
                email="pwd_change@example.com",
                username="pwd_change",
                first_name="Test",
                last_name="User",
                password="Password123!",
            )
        )

        updated_user = await repo.update_password(user.id, "NewPassword123!")
        assert updated_user is not None
        assert updated_user.verify_password("NewPassword123!")

        # Test not found
        assert await repo.update_password(uuid4(), "NewPassword123!") is None

    async def test_update_last_login(self, async_session):
        repo = UserRepository(async_session)
        user = await repo.create(
            UserCreate(
                email="login_update@example.com",
                username="login_update",
                first_name="Test",
                last_name="User",
                password="Password123!",
            )
        )

        updated_user = await repo.update_last_login(user.id)
        assert updated_user is not None
        assert updated_user.last_login is not None

        # Test not found
        assert await repo.update_last_login(uuid4()) is None

    async def test_verify_user(self, async_session):
        repo = UserRepository(async_session)
        user = await repo.create(
            UserCreate(
                email="verify_test@example.com",
                username="verify_test",
                first_name="Test",
                last_name="User",
                password="Password123!",
            )
        )

        updated_user = await repo.verify_user(user.id)
        assert updated_user is not None
        assert updated_user.is_verified is True

        # Test not found
        assert await repo.verify_user(uuid4()) is None

    async def test_deactivate_activate_user(self, async_session):
        repo = UserRepository(async_session)
        user = await repo.create(
            UserCreate(
                email="status_test@example.com",
                username="status_test",
                first_name="Test",
                last_name="User",
                password="Password123!",
            )
        )

        # Deactivate
        deactivated = await repo.deactivate_user(user.id)
        assert deactivated is not None
        assert deactivated.is_active is False

        # Activate
        activated = await repo.activate_user(user.id)
        assert activated is not None
        assert activated.is_active is True

        # Test not found
        assert await repo.deactivate_user(uuid4()) is None
        assert await repo.activate_user(uuid4()) is None

    async def test_make_superuser(self, async_session):
        repo = UserRepository(async_session)
        user = await repo.create(
            UserCreate(
                email="superuser_test@example.com",
                username="superuser_test",
                first_name="Test",
                last_name="User",
                password="Password123!",
            )
        )

        updated_user = await repo.make_superuser(user.id)
        assert updated_user is not None
        assert updated_user.is_superuser is True

        # Test not found
        assert await repo.make_superuser(uuid4()) is None

    async def test_delete_not_found(self, async_session):
        repo = UserRepository(async_session)
        assert await repo.delete(uuid4()) is False
