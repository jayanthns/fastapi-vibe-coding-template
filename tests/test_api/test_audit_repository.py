import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.apps.audit.repository import AuditLogRepository
from src.apps.audit.schemas import AuditLogCreate, AuditLogFilter
from src.apps.audit.models import AuditLog


@pytest.mark.asyncio
class TestAuditLogRepository:
    async def test_create_audit_log(self, async_session):
        repo = AuditLogRepository(async_session)
        audit_data = AuditLogCreate(
            action="CREATE",
            target_model="TestModel",
            target_object_id=str(uuid4()),
            actor_id=str(uuid4()),
            actor_email="test@example.com",
            ip_address="127.0.0.1",
            user_agent="TestAgent",
            changes={"field": "value"},
        )
        log = await repo.create(audit_data)
        assert log.id is not None
        assert log.action == "CREATE"
        assert log.actor_email == "test@example.com"

    async def test_get_by_id(self, async_session):
        repo = AuditLogRepository(async_session)
        audit_data = AuditLogCreate(
            action="READ",
            target_model="TestModel",
            target_object_id=str(uuid4()),
            actor_id=str(uuid4()),
            actor_email="read@example.com",
        )
        created_log = await repo.create(audit_data)

        fetched_log = await repo.get_by_id(created_log.id)
        assert fetched_log is not None
        assert fetched_log.id == created_log.id

    async def test_list_with_filters(self, async_session):
        repo = AuditLogRepository(async_session)
        actor_id = str(uuid4())
        target_id = str(uuid4())

        # Create logs
        log1 = await repo.create(
            AuditLogCreate(
                action="CREATE",
                target_model="ModelA",
                target_object_id=target_id,
                actor_id=actor_id,
                actor_email="user1@example.com",
            )
        )
        log2 = await repo.create(
            AuditLogCreate(
                action="UPDATE",
                target_model="ModelB",
                target_object_id=str(uuid4()),
                actor_id=str(uuid4()),
                actor_email="user2@example.com",
            )
        )

        # Test filter by actor_id
        logs, total = await repo.list(filters=AuditLogFilter(actor_id=actor_id))
        assert total == 1
        assert logs[0].id == log1.id

        # Test filter by actor_email
        logs, total = await repo.list(
            filters=AuditLogFilter(actor_email="user2@example.com")
        )
        assert total == 1
        assert logs[0].id == log2.id

        # Test filter by action
        logs, total = await repo.list(filters=AuditLogFilter(action="CREATE"))
        assert len(logs) >= 1
        assert any(l.id == log1.id for l in logs)

        # Test filter by target_model
        logs, total = await repo.list(filters=AuditLogFilter(target_model="ModelB"))
        assert total == 1
        assert logs[0].id == log2.id

        # Test filter by target_object_id
        logs, total = await repo.list(
            filters=AuditLogFilter(target_object_id=target_id)
        )
        assert total == 1
        assert logs[0].id == log1.id

    async def test_list_date_filters(self, async_session):
        repo = AuditLogRepository(async_session)

        # Create logs with different timestamps (mocking might be needed for precise control,
        # but here we rely on execution time or just create them)
        # Since we can't easily set created_at on creation via schema (it's server default usually),
        # we might need to update it manually or just rely on current time.
        # Let's create one, wait, create another.

        log1 = await repo.create(
            AuditLogCreate(action="TEST1", target_model="T", target_object_id="1")
        )

        # Manually update created_at to the past
        past_time = datetime.utcnow() - timedelta(days=1)
        log1.created_at = past_time
        await async_session.commit()

        log2 = await repo.create(
            AuditLogCreate(action="TEST2", target_model="T", target_object_id="2")
        )

        # Filter start_date
        logs, _ = await repo.list(
            filters=AuditLogFilter(start_date=datetime.utcnow() - timedelta(hours=1))
        )
        # Should include log2 but not log1
        ids = [l.id for l in logs]
        assert log2.id in ids
        assert log1.id not in ids

        # Filter end_date
        logs, _ = await repo.list(
            filters=AuditLogFilter(end_date=datetime.utcnow() - timedelta(hours=1))
        )
        # Should include log1 but not log2
        ids = [l.id for l in logs]
        assert log1.id in ids
        assert log2.id not in ids

    async def test_get_by_target(self, async_session):
        repo = AuditLogRepository(async_session)
        target_id = str(uuid4())
        await repo.create(
            AuditLogCreate(action="A", target_model="M", target_object_id=target_id)
        )
        await repo.create(
            AuditLogCreate(action="B", target_model="M", target_object_id=target_id)
        )
        await repo.create(
            AuditLogCreate(
                action="C", target_model="Other", target_object_id=str(uuid4())
            )
        )

        logs = await repo.get_by_target("M", target_id)
        assert len(logs) == 2

    async def test_get_by_actor(self, async_session):
        repo = AuditLogRepository(async_session)
        actor_id = str(uuid4())
        email = "actor@example.com"

        await repo.create(
            AuditLogCreate(
                action="A", target_model="M", target_object_id="1", actor_id=actor_id
            )
        )
        await repo.create(
            AuditLogCreate(
                action="B", target_model="M", target_object_id="2", actor_email=email
            )
        )

        # By ID
        logs = await repo.get_by_actor(actor_id=actor_id)
        assert len(logs) == 1
        assert logs[0].actor_id == actor_id

        # By Email
        logs = await repo.get_by_actor(actor_email=email)
        assert len(logs) == 1
        assert logs[0].actor_email == email

        # Both
        logs = await repo.get_by_actor(actor_id=actor_id, actor_email=email)
        # Should be empty as no single log matches both AND conditions if we look at implementation?
        # Let's check implementation:
        # if actor_id: conditions.append(AuditLog.actor_id == actor_id)
        # if actor_email: conditions.append(AuditLog.actor_email == actor_email)
        # It uses AND. So we need a log with BOTH.

        await repo.create(
            AuditLogCreate(
                action="C",
                target_model="M",
                target_object_id="3",
                actor_id=actor_id,
                actor_email=email,
            )
        )

        logs = await repo.get_by_actor(actor_id=actor_id, actor_email=email)
        assert len(logs) == 1

        # None
        logs = await repo.get_by_actor()
        assert len(logs) == 0
