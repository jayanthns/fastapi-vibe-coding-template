#!/usr/bin/env python3
"""
Script to load sensitive field data from JSON file into the database.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sensitive_fields.repository import SensitiveFieldRepository
from src.apps.sensitive_fields.schemas import SensitiveFieldCreate
from src.core.config import settings
from src.db.session import get_db


async def load_sensitive_fields_from_json(json_file_path: str) -> None:
    """Load sensitive field data from JSON file into the database."""

    # Read the JSON file
    try:
        with open(json_file_path, "r") as f:
            sensitive_fields_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file {json_file_path}: {e}")
        return

    print(f"Found {len(sensitive_fields_data)} sensitive field entries to load")

    # Get database session
    async for db in get_db():
        repository = SensitiveFieldRepository(db)

        loaded_count = 0
        skipped_count = 0

        for field_data in sensitive_fields_data:
            try:
                # Check if field already exists
                existing_field = await repository.get_by_field_name(
                    field_data["field_name"]
                )

                if existing_field:
                    print(f"⚠️  Skipping '{field_data['field_name']}' - already exists")
                    skipped_count += 1
                    continue

                # Create new sensitive field
                sensitive_field_create = SensitiveFieldCreate(**field_data)
                new_field = await repository.create(sensitive_field_create)

                print(f"✅ Loaded: '{new_field.field_name}' (ID: {new_field.id})")
                loaded_count += 1

            except Exception as e:
                print(
                    f"❌ Error loading '{field_data.get('field_name', 'unknown')}': {e}"
                )

        print(f"\n📊 Summary:")
        print(f"   Loaded: {loaded_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total: {len(sensitive_fields_data)}")


async def main():
    """Main function to run the script."""

    # Default JSON file path
    default_json_path = "data/sensitive_fields.json"

    # Check if custom path provided
    json_file_path = sys.argv[1] if len(sys.argv) > 1 else default_json_path

    # Check if file exists
    if not Path(json_file_path).exists():
        print(f"Error: File {json_file_path} does not exist")
        print(f"Usage: python {sys.argv[0]} [path_to_json_file]")
        print(f"Default: {default_json_path}")
        return

    print(f"🚀 Loading sensitive fields from: {json_file_path}")
    print(f"📊 Database: {settings.database_url}")

    await load_sensitive_fields_from_json(json_file_path)


if __name__ == "__main__":
    asyncio.run(main())
