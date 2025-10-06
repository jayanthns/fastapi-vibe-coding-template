#!/usr/bin/env python3
"""
Migration script to update existing models to use base model classes.

This script helps migrate existing database models to use the new base model
classes while maintaining data integrity and existing functionality.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from src.core.logging import get_logger
from src.db.session import get_db_session

logger = get_logger(__name__)


def check_table_exists(session, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = session.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            )
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar()


def get_table_columns(session, table_name: str) -> list[str]:
    """Get all column names for a table."""
    result = session.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = :table_name
            ORDER BY ordinal_position
        """
        ),
        {"table_name": table_name},
    )
    return [row[0] for row in result.fetchall()]


def check_column_exists(session, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    result = session.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            )
        """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar()


def add_missing_columns(session, table_name: str):
    """Add missing base model columns to existing tables."""
    logger.info(f"Checking table: {table_name}")

    if not check_table_exists(session, table_name):
        logger.warning(f"Table {table_name} does not exist, skipping")
        return

    columns = get_table_columns(session, table_name)
    logger.info(f"Existing columns: {columns}")

    # Check for missing base model columns
    missing_columns = []

    # Check for created_at
    if "created_at" not in columns:
        missing_columns.append(
            """
            ALTER TABLE {} ADD COLUMN created_at TIMESTAMP WITH TIME ZONE
            DEFAULT NOW() NOT NULL
        """.format(
                table_name
            )
        )

    # Check for updated_at
    if "updated_at" not in columns:
        missing_columns.append(
            """
            ALTER TABLE {} ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE
            DEFAULT NOW() NOT NULL
        """.format(
                table_name
            )
        )

    # Check for id column (UUID)
    if "id" not in columns:
        missing_columns.append(
            """
            ALTER TABLE {} ADD COLUMN id UUID DEFAULT gen_random_uuid()
            PRIMARY KEY
        """.format(
                table_name
            )
        )

    # Execute missing column additions
    for sql in missing_columns:
        try:
            logger.info(f"Executing: {sql.strip()}")
            session.execute(text(sql))
            session.commit()
            logger.info("Successfully added column")
        except Exception as e:
            logger.error(f"Failed to add column: {e}")
            session.rollback()

    # Add indexes for new columns
    if "created_at" not in columns:
        try:
            session.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_created_at ON {table_name} (created_at)"
                )
            )
            session.commit()
            logger.info(f"Added index for created_at on {table_name}")
        except Exception as e:
            logger.error(f"Failed to add index: {e}")
            session.rollback()

    if "updated_at" not in columns:
        try:
            session.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_updated_at ON {table_name} (updated_at)"
                )
            )
            session.commit()
            logger.info(f"Added index for updated_at on {table_name}")
        except Exception as e:
            logger.error(f"Failed to add index: {e}")
            session.rollback()


def update_updated_at_trigger(session, table_name: str):
    """Create or update the updated_at trigger for a table."""
    if not check_table_exists(session, table_name):
        return

    # Create the trigger function if it doesn't exist
    trigger_function_sql = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """

    try:
        session.execute(text(trigger_function_sql))
        session.commit()
        logger.info("Created/updated trigger function")
    except Exception as e:
        logger.error(f"Failed to create trigger function: {e}")
        session.rollback()
        return

    # Create the trigger for the table
    trigger_sql = f"""
        DROP TRIGGER IF EXISTS update_{table_name}_updated_at ON {table_name};
        CREATE TRIGGER update_{table_name}_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """

    try:
        session.execute(text(trigger_sql))
        session.commit()
        logger.info(f"Created/updated trigger for {table_name}")
    except Exception as e:
        logger.error(f"Failed to create trigger for {table_name}: {e}")
        session.rollback()


def migrate_tables():
    """Migrate all existing tables to use base model patterns."""
    logger.info("Starting migration to base models...")

    # List of tables to migrate
    tables_to_migrate = ["articles", "users", "sensitive_fields"]

    with get_db_session() as session:
        try:
            for table_name in tables_to_migrate:
                logger.info(f"Migrating table: {table_name}")
                add_missing_columns(session, table_name)
                update_updated_at_trigger(session, table_name)
                logger.info(f"Completed migration for {table_name}")

            logger.info("Migration completed successfully!")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            session.rollback()
            raise


def verify_migration():
    """Verify that the migration was successful."""
    logger.info("Verifying migration...")

    tables_to_check = ["articles", "users", "sensitive_fields"]

    with get_db_session() as session:
        for table_name in tables_to_check:
            if not check_table_exists(session, table_name):
                logger.warning(f"Table {table_name} does not exist")
                continue

            columns = get_table_columns(session, table_name)
            logger.info(f"Table {table_name} columns: {columns}")

            # Check for required base model columns
            required_columns = ["id", "created_at", "updated_at"]
            missing_columns = [col for col in required_columns if col not in columns]

            if missing_columns:
                logger.error(
                    f"Table {table_name} is missing columns: {missing_columns}"
                )
            else:
                logger.info(f"Table {table_name} has all required base model columns")


def main():
    """Main migration function."""
    logger.info("Base Models Migration Script")
    logger.info("=" * 50)

    try:
        # Run migration
        migrate_tables()

        # Verify migration
        verify_migration()

        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
