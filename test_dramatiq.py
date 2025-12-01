#!/usr/bin/env python3
"""
Test script for Dramatiq audit logging.
Run this after starting FastAPI and Dramatiq worker locally.
"""
import json
import time

import requests


def test_hello_world():
    """Test simple hello world task."""
    print("\n=== Testing Hello World Task ===")

    # Configure Dramatiq broker before importing tasks
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker

    from src.core.config import settings

    redis_broker = RedisBroker(url=settings.redis_url)
    dramatiq.set_broker(redis_broker)

    # Now import the task
    from src.test_tasks import hello_world

    print("Sending hello_world task...")
    hello_world.send("Dramatiq Test")
    print("✅ Task sent! Check worker terminal for output.")
    time.sleep(2)


def test_audit_logging():
    """Test audit logging via animal creation."""
    print("\n=== Testing Audit Logging ===")

    # Create an animal
    print("Creating animal...")
    response = requests.post(
        "http://localhost:8000/api/v1/animals/",
        json={"name": "Test Dog", "species": "Dog", "age": 5},
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 201:
        animal = response.json()["data"]
        print(f"✅ Animal created: {animal['name']} (ID: {animal['id']})")
        print("   Audit event should be queued...")

        # Wait for worker to process
        print("   Waiting 3 seconds for worker to process...")
        time.sleep(3)

        # Check audit logs
        print("   Checking audit logs...")
        audit_response = requests.get("http://localhost:8000/api/v1/audit/")
        audit_data = audit_response.json()["data"]

        if audit_data["total"] > 0:
            latest_audit = audit_data["items"][0]
            print("✅ Audit log found!")
            print(f"   Action: {latest_audit['action']}")
            print(f"   Target: {latest_audit['target_model']} ({latest_audit['target_object_id']})")
            print(f"   Changes: {json.dumps(latest_audit['changes'], indent=2)}")
        else:
            print("❌ No audit logs found - check worker for errors!")
    else:
        print(f"❌ Failed to create animal: {response.status_code}")
        print(f"   Response: {response.text}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Dramatiq Audit Logging Test Suite")
    print("=" * 60)
    print("\nMake sure you have:")
    print("  1. Redis & Postgres running in Docker")
    print("  2. FastAPI running locally (Terminal 1)")
    print("  3. Dramatiq worker running locally (Terminal 2)")
    print("=" * 60)

    try:
        # Test hello world first
        test_hello_world()

        # Test audit logging
        test_audit_logging()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  - Is FastAPI running on http://localhost:8000?")
        print("  - Is the Dramatiq worker running?")
        print("  - Check worker terminal for error messages")


if __name__ == "__main__":
    main()
