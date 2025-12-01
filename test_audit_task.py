#!/usr/bin/env python3
"""
Simple test to verify Dramatiq audit logging works.
Run this with FastAPI and Dramatiq worker running.
"""
import time


def test_audit_task_directly():
    """Test audit task directly without API."""
    print("=" * 60)
    print("Testing Audit Logging Task Directly")
    print("=" * 60)

    # Configure broker
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker

    from src.core.config import settings

    redis_broker = RedisBroker(url=settings.redis_url)
    dramatiq.set_broker(redis_broker)

    # Import audit task
    from src.apps.audit.tasks import write_audit_log

    # Create test audit payload
    test_payload = {
        "action": "CREATE",
        "target_model": "TestModel",
        "target_object_id": "test-123",
        "actor_id": "test-user-id",
        "actor_email": "test@example.com",
        "changes": {"name": "Test", "value": 42},
        "ip_address": "127.0.0.1",
        "user_agent": "TestScript/1.0",
    }

    print("\n✅ Sending audit log task to queue...")
    write_audit_log.send(test_payload)
    print("✅ Task sent!")

    print("\nCheck the worker terminal - you should see the task being processed.")
    print("Waiting 3 seconds...")
    time.sleep(3)

    print("\n✅ Test complete!")
    print("\nTo verify the audit log was created:")
    print("  curl http://localhost:8000/api/v1/audit/ | python3 -m json.tool")
    print("\nOr check the database:")
    print(
        "  docker compose exec fastapi_vibe_coding_db_svc psql -U postgres -d fastapi_vibe_coding"
    )
    print("  SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 1;")


if __name__ == "__main__":
    test_audit_task_directly()
