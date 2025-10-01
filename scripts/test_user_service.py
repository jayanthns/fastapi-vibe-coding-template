#!/usr/bin/env python3
"""
Test script for user service functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.user import UserService
from app.utils.security import get_password_hash, verify_password


async def test_user_service():
    """Test basic user service functionality."""

    print("🧪 Testing User Service")
    print("=" * 40)

    # Test password hashing
    print("\n1. Testing password hashing...")
    test_password = "TestPassword123!"
    hashed = get_password_hash(test_password)
    print(f"   Original: {test_password}")
    print(f"   Hashed: {hashed[:20]}...")

    is_valid = verify_password(test_password, hashed)
    print(f"   Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")

    # Test user creation
    print("\n2. Testing user creation...")
    async for db in get_db():
        repository = UserRepository(db)
        service = UserService(repository)

        try:
            # Create test user with unique email
            import time
            unique_email = f"test_{int(time.time())}@example.com"
            user_data = UserCreate(
                email=unique_email,
                username=f"testuser_{int(time.time())}",
                password="TestPassword123!",
                first_name="Test",
                last_name="User",
                age=25,
            )

            user, token = await service.create_user(user_data)
            print(f"   ✅ User created: {user.username} (ID: {user.id})")
            print(f"   ✅ Token generated: {token[:20]}...")

            # Test authentication
            print("\n3. Testing user authentication...")
            from app.schemas.user import UserLogin

            login_data = UserLogin(
                email=unique_email, password="TestPassword123!"
            )
            auth_user, auth_token = await service.authenticate_user(login_data)
            print(f"   ✅ Authentication successful: {auth_user.username}")

            # Test user retrieval
            print("\n4. Testing user retrieval...")
            retrieved_user = await service.get_user_by_id(user.id)
            if retrieved_user:
                print(f"   ✅ User retrieved: {retrieved_user.username}")
            else:
                print("   ❌ User retrieval failed")

            print("\n✅ All tests passed!")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        break  # Exit the async generator


if __name__ == "__main__":
    asyncio.run(test_user_service())
