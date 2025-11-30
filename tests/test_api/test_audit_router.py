import pytest
from uuid import uuid4
from src.apps.audit.repository import AuditLogRepository
from src.apps.audit.models import AuditLog


@pytest.mark.asyncio
class TestAuditRouter:
    async def test_list_audit_logs(self, async_client, async_session):
        repo = AuditLogRepository(async_session)
        audit1 = AuditLog(
            action="create",
            target_model="user",
            target_object_id="user_1",
            actor_id="actor_1",
            actor_email="actor1@example.com",
            changes={"field": "value"},
        )
        audit2 = AuditLog(
            action="update",
            target_model="user",
            target_object_id="user_2",
            actor_id="actor_2",
            actor_email="actor2@example.com",
            changes={"field": "new_value"},
        )
        async_session.add(audit1)
        async_session.add(audit2)
        await async_session.commit()

        response = await async_client.get("/api/v1/audit/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) >= 2

        # Test filters
        response = await async_client.get("/api/v1/audit/", params={"action": "create"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) == 1
        assert data["items"][0]["action"] == "create"

    async def test_get_audit_log(self, async_client, async_session):
        repo = AuditLogRepository(async_session)
        audit = AuditLog(
            action="delete",
            target_model="post",
            target_object_id="post_1",
            actor_id="actor_3",
            actor_email="actor3@example.com",
            changes={},
        )
        async_session.add(audit)
        await async_session.commit()

        response = await async_client.get(f"/api/v1/audit/{audit.id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == str(audit.id)
        assert data["action"] == "delete"

    async def test_get_audit_log_not_found(self, async_client):
        response = await async_client.get(f"/api/v1/audit/{uuid4()}")
        assert response.status_code == 404

    async def test_get_target_history(self, async_client, async_session):
        repo = AuditLogRepository(async_session)
        audit1 = AuditLog(
            action="create",
            target_model="comment",
            target_object_id="comment_1",
            actor_id="actor_4",
            actor_email="actor4@example.com",
            changes={},
        )
        audit2 = AuditLog(
            action="update",
            target_model="comment",
            target_object_id="comment_1",
            actor_id="actor_4",
            actor_email="actor4@example.com",
            changes={},
        )
        async_session.add(audit1)
        async_session.add(audit2)
        await async_session.commit()

        response = await async_client.get("/api/v1/audit/target/comment/comment_1")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

    async def test_get_actor_history(self, async_client, async_session):
        repo = AuditLogRepository(async_session)
        audit = AuditLog(
            action="login",
            target_model="session",
            target_object_id="session_1",
            actor_id="actor_5",
            actor_email="actor5@example.com",
            changes={},
        )
        async_session.add(audit)
        await async_session.commit()

        response = await async_client.get(
            "/api/v1/audit/actor/history", params={"actor_id": "actor_5"}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["actor_id"] == "actor_5"

        response = await async_client.get(
            "/api/v1/audit/actor/history", params={"actor_email": "actor5@example.com"}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["actor_email"] == "actor5@example.com"

    async def test_get_actor_history_bad_request(self, async_client):
        response = await async_client.get("/api/v1/audit/actor/history")
        assert response.status_code == 400
