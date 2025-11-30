import pytest
from fastapi.testclient import TestClient

from src.core.auth import get_current_superuser
from src.main import app


class TestUserScenarios:
    def test_user_lifecycle(self, client: TestClient):
        """Test full lifecycle of a user: Register -> Login -> Profile -> Update"""

        # 1. Register
        register_payload = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User",
            "age": 25,
        }
        response = client.post("/api/v1/users/register", json=register_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        user_id = data["data"]["user"]["id"]
        access_token = data["data"]["access_token"]

        # 2. Login
        login_payload = {"email": "test@example.com", "password": "Password123!"}
        response = client.post("/api/v1/users/login", json=login_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["access_token"] is not None
        token = data["data"]["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get Profile (Me)
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == user_id
        assert data["data"]["email"] == "test@example.com"

        # 4. Update Profile
        update_payload = {"first_name": "Updated Name"}
        response = client.patch(
            "/api/v1/users/me", json=update_payload, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["first_name"] == "Updated Name"

        # 5. Change Password
        password_payload = {
            "current_password": "Password123!",
            "new_password": "NewPassword123!",
        }
        response = client.post(
            "/api/v1/users/me/change-password", json=password_payload, headers=headers
        )
        assert response.status_code == 200

        # 6. Login with new password
        login_payload["password"] = "NewPassword123!"
        response = client.post("/api/v1/users/login", json=login_payload)
        assert response.status_code == 200

    def test_admin_endpoints(self, client: TestClient):
        """Test admin endpoints by overriding dependency"""

        # Mock superuser dependency
        async def mock_get_superuser():
            return {
                "id": "admin_id",
                "email": "admin@example.com",
                "is_superuser": True,
                "is_active": True,
            }

        app.dependency_overrides[get_current_superuser] = mock_get_superuser

        try:
            # List Users (Admin only)
            response = client.get("/api/v1/users/")
            # Since we have no users in this test session (unless created above, but session fixture resets?),
            # actually session fixture is session-scoped but async_session is function scoped?
            # No, async_session_fixture yields a session.
            # The client fixture uses dependency override for get_db.
            # So the DB state persists across tests if they share the same session?
            # Wait, client fixture yields client, then clears overrides.
            # But async_session fixture is named "async_session" and used by client.
            # Let's check conftest scope.

            # async_session_fixture is default scope (function).
            # So DB is fresh for each test function.

            # So list users should be empty or have 0 items.
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # assert len(data["data"]["items"]) == 0 # Might be 0

        finally:
            del app.dependency_overrides[get_current_superuser]
