#!/usr/bin/env python3
"""
Script to check UUID column types in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402, isort:skip

from src.db.session import get_async_engine  # noqa: E402, isort:skip


async def check_uuid_columns():
    """Check the UUID column types for all tables."""

    print("📊 Checking UUID Column Types")
    print("=" * 40)

    engine = get_async_engine()

    async with engine.connect() as conn:
        # Check the column types for all tables
        result = await conn.execute(
            text(
                """
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE column_name = 'id' AND table_name IN ('articles', 'sensitive_fields', 'users')
            ORDER BY table_name;
        """
            )
        )

        rows = result.fetchall()

        if rows:
            print(f"{'Table':<20} {'Column':<10} {'Data Type':<15} {'Nullable'}")
            print("-" * 55)

            for row in rows:
                print(
                    f"{row.table_name:<20} {row.column_name:<10} {row.data_type:<15} {row.is_nullable}"
                )

            print(f"\n✅ Found {len(rows)} UUID columns")

            # Check if all are consistent
            data_types = set(row.data_type for row in rows)
            if len(data_types) == 1:
                print(f"✅ All UUID columns use consistent type: {list(data_types)[0]}")
            else:
                print(f"⚠️  UUID columns use different types: {data_types}")

        else:
            print("❌ No UUID columns found")

        # Also check the table structure
        print("\n📋 Table Structure Summary:")
        result2 = await conn.execute(
            text(
                """
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name IN ('articles', 'sensitive_fields', 'users')
            ORDER BY table_name, ordinal_position;
        """
            )
        )

        current_table = None
        for row in result2.fetchall():
            if row.table_name != current_table:
                if current_table is not None:
                    print()
                print(f"Table: {row.table_name}")
                print("-" * 30)
                current_table = row.table_name

            nullable = "NULL" if row.is_nullable == "YES" else "NOT NULL"
            print(f"  {row.column_name:<20} {row.data_type:<15} {nullable}")


if __name__ == "__main__":
    asyncio.run(check_uuid_columns())
