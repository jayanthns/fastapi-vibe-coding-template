import pytest
from fastapi.testclient import TestClient

from src.core.enums import AuditAction


class TestAuditScenarios:
    async def test_audit_lifecycle(self, client: TestClient, async_session):
        """Test full lifecycle of audit logs: List -> Get -> Filter"""
        from src.apps.audit.models import AuditLog
        from uuid import uuid4
        from datetime import datetime

        # 1. Seed Audit Log directly (since POST endpoint is removed)
        audit_id = uuid4()
        audit_log = AuditLog(
            id=audit_id,
            action=AuditAction.LOGIN.value,
            target_model="auth.User",
            target_object_id="1",
            actor_id="123",
            actor_email="test@example.com",
            ip_address="127.0.0.1",
            changes={"status": "active"},
            created_at=datetime.utcnow(),
        )
        async_session.add(audit_log)
        await async_session.commit()
        await async_session.refresh(audit_log)

        audit_id = str(audit_id)  # Convert to string for comparison

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
