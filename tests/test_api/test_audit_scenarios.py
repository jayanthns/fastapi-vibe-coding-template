import pytest
from fastapi.testclient import TestClient

from src.core.enums import AuditAction


class TestAuditScenarios:
    def test_audit_lifecycle(self, client: TestClient):
        """Test full lifecycle of audit logs: Create -> List -> Get -> Filter"""

        # 1. Create Audit Log
        create_payload = {
            "action": AuditAction.LOGIN.value,
            "target_model": "auth.User",
            "target_object_id": "1",
            "actor_id": "123",
            "actor_email": "test@example.com",
            "ip_address": "127.0.0.1",
            "changes": {"status": "active"},
        }
        response = client.post("/api/v1/audit/", json=create_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        audit_id = data["data"]["id"]
        assert data["data"]["action"] == AuditAction.LOGIN.value
        assert data["data"]["target_model"] == "auth.User"

        # 2. List Audit Logs
        response = client.get("/api/v1/audit/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) >= 1
        assert any(a["id"] == audit_id for a in data["data"]["items"])

        # 3. Get Audit Log
        response = client.get(f"/api/v1/audit/{audit_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == audit_id
        assert data["data"]["action"] == AuditAction.LOGIN.value

        # 4. Filter by Actor
        response = client.get("/api/v1/audit/", params={"actor_id": "123"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert all(a["actor_id"] == "123" for a in data["data"]["items"])

        # 5. Get Target History
        response = client.get("/api/v1/audit/target/auth.User/1")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert all(a["target_model"] == "auth.User" for a in data["data"])

        # 6. Get Actor History
        response = client.get("/api/v1/audit/actor/history", params={"actor_id": "123"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert all(a["actor_id"] == "123" for a in data["data"])
