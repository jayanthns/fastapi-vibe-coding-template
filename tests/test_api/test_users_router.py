import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import status

from src.apps.users.router import get_user_service
from src.core.auth import get_current_active_user, get_current_superuser


@pytest.fixture
def mock_user_service():
    return AsyncMock()


@pytest.fixture
def override_dependencies(app_fixture, mock_user_service):
    app = app_fixture
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    # Mock auth to bypass login for some tests
    app.dependency_overrides[get_current_active_user] = lambda: {
        "id": str(uuid4()),
        "email": "test@example.com",
        "is_active": True,
        "is_superuser": False,
    }
    app.dependency_overrides[get_current_superuser] = lambda: {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "is_active": True,
        "is_superuser": True,
    }
    yield
    app.dependency_overrides.clear()


def create_mock_user(user_id=None, email="test@example.com", **kwargs):
    user_id = user_id or uuid4()
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.email = email

    user_data = {
        "id": str(user_id),
        "email": email,
        "username": email.split("@")[0],
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
        "is_verified": False,
        "is_superuser": False,
        "last_login": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    user_data.update(kwargs)

    mock_user.model_dump.return_value = user_data
    return mock_user


@pytest.mark.asyncio
async def test_register_user_success(
    async_client, mock_user_service, override_dependencies
):
    mock_user = create_mock_user(email="new@example.com")
    mock_user_service.create_user.return_value = (mock_user, "access_token")

    response = await async_client.post(
        "/api/v1/users/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "Password123!",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["access_token"] == "access_token"


@pytest.mark.asyncio
async def test_register_user_failure(
    async_client, mock_user_service, override_dependencies
):
    mock_user_service.create_user.side_effect = ValueError("Email already registered")

    response = await async_client.post(
        "/api/v1/users/register",
        json={
            "email": "existing@example.com",
            "username": "existinguser",
            "first_name": "Existing",
            "last_name": "User",
            "password": "Password123!",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["message"]


@pytest.mark.asyncio
async def test_login_user_success(
    async_client, mock_user_service, override_dependencies
):
    mock_user = create_mock_user(email="test@example.com")
    mock_user_service.authenticate_user.return_value = (mock_user, "access_token")

    response = await async_client.post(
        "/api/v1/users/login",
        json={"email": "test@example.com", "password": "Password123!"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["access_token"] == "access_token"


@pytest.mark.asyncio
async def test_login_user_failure(
    async_client, mock_user_service, override_dependencies
):
    mock_user_service.authenticate_user.side_effect = ValueError("Invalid credentials")

    response = await async_client.post(
        "/api/v1/users/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_me_success(async_client, mock_user_service, override_dependencies):
    mock_user = create_mock_user(email="test@example.com")
    mock_user_service.get_user_by_id.return_value = mock_user

    response = await async_client.get("/api/v1/users/me")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_me_not_found(async_client, mock_user_service, override_dependencies):
    mock_user_service.get_user_by_id.return_value = None

    response = await async_client.get("/api/v1/users/me")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_me_success(
    async_client, mock_user_service, override_dependencies
):
    mock_user = create_mock_user(email="updated@example.com")
    mock_user_service.update_user.return_value = mock_user

    response = await async_client.patch(
        "/api/v1/users/me", json={"first_name": "Updated"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_change_password_success(
    async_client, mock_user_service, override_dependencies
):
    mock_user_service.change_password.return_value = True

    response = await async_client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "old", "new_password": "NewPassword123!"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_change_password_failure(
    async_client, mock_user_service, override_dependencies
):
    mock_user_service.change_password.side_effect = ValueError("Incorrect password")

    response = await async_client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "wrong", "new_password": "NewPassword123!"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_list_users_admin(async_client, mock_user_service, override_dependencies):
    mock_user_service.get_users.return_value = ([], 0)

    response = await async_client.get("/api/v1/users/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["items"] == []


@pytest.mark.asyncio
async def test_get_user_by_id_admin(
    async_client, mock_user_service, override_dependencies
):
    user_id = uuid4()
    mock_user = create_mock_user(user_id=user_id)
    mock_user_service.get_user_by_id.return_value = mock_user

    response = await async_client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["id"] == str(user_id)


@pytest.mark.asyncio
async def test_update_user_admin(
    async_client, mock_user_service, override_dependencies
):
    user_id = uuid4()
    mock_user = create_mock_user(user_id=user_id, is_active=False)
    mock_user_service.update_user.return_value = mock_user

    response = await async_client.patch(
        f"/api/v1/users/{user_id}", json={"is_active": False}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_verify_user_admin(
    async_client, mock_user_service, override_dependencies
):
    user_id = uuid4()
    mock_user = create_mock_user(user_id=user_id, is_verified=True)
    mock_user_service.verify_user.return_value = mock_user

    response = await async_client.post(f"/api/v1/users/{user_id}/verify")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["is_verified"] is True


@pytest.mark.asyncio
async def test_deactivate_user_admin(
    async_client, mock_user_service, override_dependencies
):
    user_id = uuid4()
    mock_user = create_mock_user(user_id=user_id, is_active=False)
    mock_user_service.deactivate_user.return_value = mock_user

    response = await async_client.post(f"/api/v1/users/{user_id}/deactivate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_activate_user_admin(
    async_client, mock_user_service, override_dependencies
):
    user_id = uuid4()
    mock_user = create_mock_user(user_id=user_id, is_active=True)
    mock_user_service.activate_user.return_value = mock_user

    response = await async_client.post(f"/api/v1/users/{user_id}/activate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_make_superuser_admin(
    async_client, mock_user_service, override_dependencies
):
    user_id = uuid4()
    mock_user = create_mock_user(user_id=user_id, is_superuser=True)
    mock_user_service.make_superuser.return_value = mock_user

    response = await async_client.post(f"/api/v1/users/{user_id}/make-superuser")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["is_superuser"] is True
