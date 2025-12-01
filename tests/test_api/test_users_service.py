from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.apps.users.repository import UserRepository
from src.apps.users.schemas import UserCreate, UserLogin, UserPasswordChange, UserUpdate
from src.apps.users.service import UserService


@pytest.mark.asyncio
class TestUserService:
    async def test_create_user_success(self):
        from datetime import datetime

        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_email = AsyncMock(return_value=None)
        mock_repo.get_by_username = AsyncMock(return_value=None)

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.age = 25
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user.is_verified = False
        mock_user.last_login = None
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()

        mock_repo.create = AsyncMock(return_value=mock_user)

        service = UserService(repository=mock_repo)

        user_create = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )

        user_response, token = await service.create_user(user_create)

        assert user_response.email == "test@example.com"
        assert token is not None
        mock_repo.create.assert_called_once()

    async def test_create_user_email_exists(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_email = AsyncMock(return_value=MagicMock())

        service = UserService(repository=mock_repo)

        user_create = UserCreate(
            email="existing@example.com",
            username="newuser",
            first_name="Test",
            last_name="User",
            password="Password123!",
        )

        with pytest.raises(ValueError, match="Email already registered"):
            await service.create_user(user_create)

    async def test_authenticate_user_success(self):
        from datetime import datetime

        mock_repo = MagicMock(spec=UserRepository)

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.age = 25
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user.is_verified = False
        mock_user.last_login = datetime.utcnow()
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()
        mock_user.verify_password.return_value = True

        mock_repo.get_by_email_or_username = AsyncMock(return_value=mock_user)
        mock_repo.update_last_login = AsyncMock()

        service = UserService(repository=mock_repo)

        user_login = UserLogin(email="test@example.com", password="Password123!")
        user_response, token = await service.authenticate_user(user_login)

        assert user_response.email == "test@example.com"
        assert token is not None
        mock_repo.update_last_login.assert_called_once()

    async def test_authenticate_user_invalid_credentials(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_email_or_username = AsyncMock(return_value=None)

        service = UserService(repository=mock_repo)

        user_login = UserLogin(email="wrong@example.com", password="Password123!")

        with pytest.raises(ValueError, match="Invalid credentials"):
            await service.authenticate_user(user_login)

    async def test_change_password_success(self):
        mock_repo = MagicMock(spec=UserRepository)
        user_id = uuid4()

        mock_user = MagicMock()
        mock_user.verify_password.return_value = True
        mock_repo.get_by_id = AsyncMock(return_value=mock_user)
        mock_repo.update_password = AsyncMock(return_value=mock_user)

        service = UserService(repository=mock_repo)

        change_data = UserPasswordChange(
            current_password="oldpass",
            new_password="NewPassword123!",
        )

        result = await service.change_password(user_id, change_data)
        assert result is True
        mock_repo.update_password.assert_called_once()

    async def test_authenticate_user_deactivated(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_user = MagicMock()
        mock_user.verify_password.return_value = True
        mock_user.is_active = False

        mock_repo.get_by_email_or_username = AsyncMock(return_value=mock_user)

        service = UserService(repository=mock_repo)
        user_login = UserLogin(email="test@example.com", password="Password123!")

        with pytest.raises(ValueError, match="Account is deactivated"):
            await service.authenticate_user(user_login)

    async def test_get_user_by_id_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)

        service = UserService(repository=mock_repo)
        result = await service.get_user_by_id(uuid4())
        assert result is None

    async def test_update_user_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.update = AsyncMock(return_value=None)

        service = UserService(repository=mock_repo)
        result = await service.update_user(uuid4(), UserUpdate(first_name="New"))
        assert result is None

    async def test_change_password_user_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)

        service = UserService(repository=mock_repo)
        result = await service.change_password(
            uuid4(),
            UserPasswordChange(current_password="old", new_password="NewPassword123!"),
        )
        assert result is False

    async def test_change_password_incorrect_current(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_user = MagicMock()
        mock_user.verify_password.return_value = False
        mock_repo.get_by_id = AsyncMock(return_value=mock_user)

        service = UserService(repository=mock_repo)
        with pytest.raises(ValueError, match="Current password is incorrect"):
            await service.change_password(
                uuid4(),
                UserPasswordChange(current_password="wrong", new_password="NewPassword123!"),
            )

    async def test_verify_user_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.verify_user = AsyncMock(return_value=None)
        service = UserService(repository=mock_repo)
        assert await service.verify_user(uuid4()) is None

    async def test_deactivate_user_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.deactivate_user = AsyncMock(return_value=None)
        service = UserService(repository=mock_repo)
        assert await service.deactivate_user(uuid4()) is None

    async def test_activate_user_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.activate_user = AsyncMock(return_value=None)
        service = UserService(repository=mock_repo)
        assert await service.activate_user(uuid4()) is None

    async def test_make_superuser_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.make_superuser = AsyncMock(return_value=None)
        service = UserService(repository=mock_repo)
        assert await service.make_superuser(uuid4()) is None

    async def test_get_users(self):
        from datetime import datetime

        mock_repo = MagicMock(spec=UserRepository)
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.age = 25
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user.is_verified = False
        mock_user.last_login = None
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()

        mock_repo.get_all = AsyncMock(return_value=([mock_user], 1))

        service = UserService(repository=mock_repo)
        users, total = await service.get_users()
        assert len(users) == 1
        assert total == 1

    async def test_create_token_pair(self):
        service = UserService(repository=MagicMock())
        with (
            patch("src.apps.users.service.create_access_token") as mock_access,
            patch("src.apps.users.service.create_refresh_token") as mock_refresh,
        ):
            mock_access.return_value = "access"
            mock_refresh.return_value = "refresh"

            access, refresh = await service.create_token_pair(uuid4(), "test@example.com")
            assert access == "access"
            assert refresh == "refresh"

    async def test_refresh_access_token_invalid_token(self):
        service = UserService(repository=MagicMock())
        with patch("src.utils.security.verify_token", return_value=None):
            assert await service.refresh_access_token("invalid") is None

    async def test_refresh_access_token_wrong_type(self):
        service = UserService(repository=MagicMock())
        with patch("src.utils.security.verify_token", return_value={"type": "access"}):
            assert await service.refresh_access_token("token") is None

    async def test_refresh_access_token_user_not_found(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)
        service = UserService(repository=mock_repo)

        with patch(
            "src.utils.security.verify_token",
            return_value={
                "sub": str(uuid4()),
                "email": "test@example.com",
                "type": "refresh",
            },
        ):
            assert await service.refresh_access_token("token") is None

    async def test_refresh_access_token_user_inactive(self):
        mock_repo = MagicMock(spec=UserRepository)
        mock_user = MagicMock()
        mock_user.is_active = False
        mock_repo.get_by_id = AsyncMock(return_value=mock_user)
        service = UserService(repository=mock_repo)

        with patch(
            "src.utils.security.verify_token",
            return_value={
                "sub": str(uuid4()),
                "email": "test@example.com",
                "type": "refresh",
            },
        ):
            assert await service.refresh_access_token("token") is None
