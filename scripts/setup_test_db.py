#!/usr/bin/env python3
"""
Setup script for test PostgreSQL database.

This script creates a test database for running tests.
"""

import asyncio

# Test database configuration - read from environment
import os
import sys
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine


def get_database_urls():
    """Get database URLs from environment variables."""
    # Get database credentials from environment
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = os.getenv("DATABASE_PORT", "5432")
    db_user = os.getenv("DATABASE_USERNAME", "postgres")
    db_password = os.getenv("DATABASE_PASSWORD", "postgres")
    db_name = os.getenv("DATABASE_NAME", "fastapi_vibe_coding")

    # Create test database name
    test_db_name = f"{db_name}_test"

    # URL encode password to handle special characters
    encoded_password = quote_plus(db_password)

    # Admin database URL (connects to default postgres database)
    admin_url = f"postgresql+asyncpg://{db_user}:{encoded_password}@{db_host}:{db_port}/postgres"

    # Test database URL
    test_url = f"postgresql+asyncpg://{db_user}:{encoded_password}@{db_host}:{db_port}/{test_db_name}"

    return admin_url, test_url, test_db_name


ADMIN_DATABASE_URL, TEST_DATABASE_URL, TEST_DB_NAME = get_database_urls()


async def setup_test_database():
    """Create test database if it doesn't exist."""
    print("Setting up test database...")

    # Connect to admin database to create test database
    admin_engine = create_async_engine(ADMIN_DATABASE_URL, echo=False)

    try:
        # Check if test database exists
        async with admin_engine.connect() as conn:
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
            )

            if result.fetchone():
                print(f"✅ Test database '{TEST_DB_NAME}' already exists")
            else:
                # Create test database (outside transaction)
                await conn.execute(text("COMMIT"))  # End any existing transaction
                await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
                print(f"✅ Created test database '{TEST_DB_NAME}'")

    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        sys.exit(1)
    finally:
        await admin_engine.dispose()

    # Test connection to the new database
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    try:
        async with test_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Successfully connected to test database")
    except Exception as e:
        print(f"❌ Error connecting to test database: {e}")
        sys.exit(1)
    finally:
        await test_engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_test_database())
