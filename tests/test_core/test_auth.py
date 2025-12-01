from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from src.core.auth import (
    get_current_active_user,
    get_current_superuser,
    get_current_user,
    get_optional_current_user,
)


@pytest.fixture
def mock_credentials():
    credentials = MagicMock()
    credentials.credentials = "fake_token"
    return credentials


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_current_user_success(mock_credentials, mock_db):
    user_id = uuid4()
    with patch("src.core.auth.verify_token") as mock_verify:
        mock_verify.return_value = {"sub": str(user_id)}

        with patch("src.core.auth.UserRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            MockRepo.return_value = mock_repo_instance

            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.email = "test@example.com"
            mock_user.username = "testuser"
            mock_user.is_active = True
            mock_user.is_verified = True
            mock_user.is_superuser = False

            mock_repo_instance.get_by_id.return_value = mock_user

            user = await get_current_user(mock_credentials, mock_db)

            assert user["id"] == user_id
            assert user["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_credentials, mock_db):
    with patch("src.core.auth.verify_token") as mock_verify:
        mock_verify.return_value = None

        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_credentials, mock_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_no_sub(mock_credentials, mock_db):
    with patch("src.core.auth.verify_token") as mock_verify:
        mock_verify.return_value = {"other": "claim"}

        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_credentials, mock_db)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_not_found(mock_credentials, mock_db):
    user_id = uuid4()
    with patch("src.core.auth.verify_token") as mock_verify:
        mock_verify.return_value = {"sub": str(user_id)}

        with patch("src.core.auth.UserRepository") as MockRepo:
            mock_repo_instance = AsyncMock()
            MockRepo.return_value = mock_repo_instance
            mock_repo_instance.get_by_id.return_value = None

            with pytest.raises(HTTPException) as exc:
                await get_current_user(mock_credentials, mock_db)

            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_active_user_success():
    user = {"is_active": True}
    result = await get_current_active_user(user)
    assert result == user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    user = {"is_active": False}
    with pytest.raises(HTTPException) as exc:
        await get_current_active_user(user)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_get_current_superuser_success():
    user = {"is_superuser": True}
    result = await get_current_superuser(user)
    assert result == user


@pytest.mark.asyncio
async def test_get_current_superuser_failure():
    user = {"is_superuser": False}
    with pytest.raises(HTTPException) as exc:
        await get_current_superuser(user)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Not enough permissions"


@pytest.mark.asyncio
async def test_get_optional_current_user_none(mock_db):
    result = await get_optional_current_user(None, mock_db)
    assert result is None


@pytest.mark.asyncio
async def test_get_optional_current_user_success(mock_credentials, mock_db):
    with patch("src.core.auth.get_current_user") as mock_get_user:
        mock_get_user.return_value = {"id": "user"}

        result = await get_optional_current_user(mock_credentials, mock_db)
        assert result == {"id": "user"}


@pytest.mark.asyncio
async def test_get_optional_current_user_failure(mock_credentials, mock_db):
    with patch("src.core.auth.get_current_user") as mock_get_user:
        mock_get_user.side_effect = HTTPException(status_code=401)

        result = await get_optional_current_user(mock_credentials, mock_db)
        assert result is None
