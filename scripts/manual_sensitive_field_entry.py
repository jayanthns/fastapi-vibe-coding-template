#!/usr/bin/env python3
"""
Interactive script to manually add sensitive field entries to the database.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import get_db
from app.repositories.sensitive_field import SensitiveFieldRepository
from app.schemas.sensitive_field import SensitiveFieldCreate


async def add_sensitive_field_interactive():
    """Interactive function to add sensitive field entries."""

    async for db in get_db():
        repository = SensitiveFieldRepository(db)

        print("🔧 Manual Sensitive Field Entry")
        print("=" * 40)

        while True:
            print("\n📝 Enter sensitive field details:")

            field_name = input("Field name/pattern: ").strip()
            if not field_name:
                print("❌ Field name cannot be empty")
                continue

            # Check if already exists
            existing = await repository.get_by_field_name(field_name)
            if existing:
                print(f"⚠️  Field '{field_name}' already exists (ID: {existing.id})")
                continue

            is_exact_match_input = (
                input("Is exact match? (y/n, default: y): ").strip().lower()
            )
            is_exact_match = is_exact_match_input != "n"

            is_active_input = input("Is active? (y/n, default: y): ").strip().lower()
            is_active = is_active_input != "n"

            description = input("Description (optional): ").strip()

            try:
                # Create the sensitive field
                sensitive_field_data = SensitiveFieldCreate(
                    field_name=field_name,
                    is_exact_match=is_exact_match,
                    is_active=is_active,
                    description=description if description else None,
                )

                new_field = await repository.create(sensitive_field_data)

                print(f"✅ Successfully created sensitive field:")
                print(f"   ID: {new_field.id}")
                print(f"   Field Name: {new_field.field_name}")
                print(f"   Exact Match: {new_field.is_exact_match}")
                print(f"   Active: {new_field.is_active}")
                print(f"   Description: {new_field.description}")

            except Exception as e:
                print(f"❌ Error creating sensitive field: {e}")

            # Ask if user wants to continue
            continue_input = input("\nAdd another field? (y/n): ").strip().lower()
            if continue_input == "n":
                break

        print("\n👋 Done!")


async def list_existing_fields():
    """List all existing sensitive fields."""

    async for db in get_db():
        repository = SensitiveFieldRepository(db)

        print("\n📋 Existing Sensitive Fields:")
        print("=" * 50)

        try:
            fields, total = await repository.get_all(limit=1000)  # Get all fields

            if total == 0:
                print("No sensitive fields found in database.")
                return

            for field in fields:
                match_type = "Exact" if field.is_exact_match else "Regex"
                status = "Active" if field.is_active else "Inactive"
                print(f"🆔 {field.id}")
                print(f"   Field: {field.field_name}")
                print(f"   Type: {match_type}")
                print(f"   Status: {status}")
                print(f"   Description: {field.description}")
                print(f"   Created: {field.created_at}")
                print("-" * 30)

            print(f"\n📊 Total: {total} sensitive fields")

        except Exception as e:
            print(f"❌ Error listing fields: {e}")


async def main():
    """Main function."""

    print("🔧 Sensitive Field Management Tool")
    print("=" * 40)

    while True:
        print("\nChoose an option:")
        print("1. Add new sensitive field")
        print("2. List existing sensitive fields")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            await add_sensitive_field_interactive()
        elif choice == "2":
            await list_existing_fields()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    asyncio.run(main())
