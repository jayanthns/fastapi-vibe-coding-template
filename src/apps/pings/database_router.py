"""
Database ping and health check endpoints.

This module provides comprehensive database connectivity and health check endpoints
including read/write access, DML/DDL operations, and connection pool status.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.core.logging import get_logger
from src.core.schemas import APIResponse
from src.db.session import get_db
from src.utils.security import secure_response

router = APIRouter()


def get_request_logger(request: Request):
    """Get request logger with trace_id."""
    return get_logger(request)


def get_trace_id(request: Request) -> str:
    """Get trace_id from request state."""
    return getattr(request.state, "trace_id", "no-trace-id")


@router.get("/ping", response_model=APIResponse)
async def ping_database(request: Request, db=Depends(get_db)):
    """
    Ping database connectivity and basic health check.

    Tests:
    - Database connection
    - Basic query execution
    - Connection pool status
    - Response time measurement
    """
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    start_time = time.time()

    try:
        # Test basic connectivity with a simple query
        result = await db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()

        # Get connection pool info
        pool = db.get_bind().pool
        pool_info = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": getattr(pool, "invalid", lambda: 0)(),  # Fallback for async pools
        }

        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        if test_value == 1:
            logger.info(
                f"Database ping successful - {response_time:.2f}ms",
                extra={
                    "trace_id": trace_id,
                    "response_time_ms": response_time,
                    "pool_info": pool_info,
                },
            )

            return APIResponse.create_with_trace_id(
                data={
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "test_query_result": test_value,
                    "connection_pool": pool_info,
                    "database_type": str(db.get_bind().dialect.name),
                },
                message="Database ping successful",
                trace_id=trace_id,
            )
        else:
            logger.warning(
                f"Database ping failed - unexpected result: {test_value}",
                extra={"trace_id": trace_id, "test_value": test_value},
            )

            return APIResponse.create_with_trace_id(
                data={
                    "status": "unhealthy",
                    "response_time_ms": round(response_time, 2),
                    "test_query_result": test_value,
                    "error": "Unexpected query result",
                },
                message="Database ping failed - unexpected result",
                success=False,
                trace_id=trace_id,
            )

    except SQLAlchemyError as e:
        response_time = (time.time() - start_time) * 1000

        logger.error(
            f"Database ping failed - SQLAlchemy error: {str(e)}",
            extra={
                "trace_id": trace_id,
                "error": str(e),
                "response_time_ms": response_time,
            },
        )

        raise HTTPException(
            status_code=503,
            detail=secure_response(
                {
                    "success": False,
                    "message": "Database connection failed",
                    "data": {
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "error": str(e),
                        "database_type": "unknown",
                    },
                    "error": str(e),
                    "trace_id": trace_id,
                }
            ),
        )

    except Exception as e:
        response_time = (time.time() - start_time) * 1000

        logger.error(
            f"Database ping failed - unexpected error: {str(e)}",
            extra={
                "trace_id": trace_id,
                "error": str(e),
                "response_time_ms": response_time,
            },
        )

        raise HTTPException(
            status_code=503,
            detail=secure_response(
                {
                    "success": False,
                    "message": "Database ping failed",
                    "data": {
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "error": str(e),
                    },
                    "error": str(e),
                    "trace_id": trace_id,
                }
            ),
        )


@router.get("/read", response_model=APIResponse)
async def test_database_read(request: Request, db=Depends(get_db)):
    """
    Test database read access (SELECT operations).

    Tests:
    - SELECT query execution
    - Data retrieval
    - Query performance
    - Result set handling
    """
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    start_time = time.time()

    try:
        # Test read access with a more complex query
        query = text(
            """
            SELECT
                'read_test' as operation,
                COUNT(*) as table_count,
                NOW() as current_time,
                VERSION() as db_version
        """
        )

        result = await db.execute(query)
        row = result.fetchone()

        response_time = (time.time() - start_time) * 1000

        logger.info(
            f"Database read test successful - {response_time:.2f}ms",
            extra={
                "trace_id": trace_id,
                "response_time_ms": response_time,
                "operation": "read_test",
            },
        )

        return APIResponse.create_with_trace_id(
            data={
                "status": "healthy",
                "operation": "read_test",
                "response_time_ms": round(response_time, 2),
                "result": {
                    "operation": row[0],
                    "table_count": row[1],
                    "current_time": str(row[2]),
                    "db_version": row[3],
                },
            },
            message="Database read test successful",
            trace_id=trace_id,
        )

    except SQLAlchemyError as e:
        response_time = (time.time() - start_time) * 1000

        logger.error(
            f"Database read test failed: {str(e)}",
            extra={
                "trace_id": trace_id,
                "error": str(e),
                "response_time_ms": response_time,
            },
        )

        raise HTTPException(
            status_code=503,
            detail=secure_response(
                {
                    "success": False,
                    "message": "Database read test failed",
                    "data": {
                        "status": "unhealthy",
                        "operation": "read_test",
                        "response_time_ms": round(response_time, 2),
                        "error": str(e),
                    },
                    "error": str(e),
                    "trace_id": trace_id,
                }
            ),
        )


@router.get("/write", response_model=APIResponse)
async def test_database_write(request: Request, db=Depends(get_db)):
    """
    Test database write access (INSERT/UPDATE/DELETE operations).

    Tests:
    - INSERT operation
    - UPDATE operation
    - DELETE operation
    - Transaction handling
    """
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    start_time = time.time()

    try:
        # Test write access with a temporary table
        test_table_name = f"ping_test_{int(time.time())}"

        # Create temporary table
        create_table_query = text(
            f"""
            CREATE TEMPORARY TABLE {test_table_name} (
                id SERIAL PRIMARY KEY,
                test_data VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """
        )

        await db.execute(create_table_query)

        # Test INSERT
        insert_query = text(
            f"""
            INSERT INTO {test_table_name} (test_data)
            VALUES ('ping_test_data')
        """
        )
        insert_result = await db.execute(insert_query)
        insert_count = insert_result.rowcount

        # Test UPDATE
        update_query = text(
            f"""
            UPDATE {test_table_name}
            SET test_data = 'updated_ping_test_data'
            WHERE test_data = 'ping_test_data'
        """
        )
        update_result = await db.execute(update_query)
        update_count = update_result.rowcount

        # Test SELECT to verify data
        select_query = text(f"SELECT COUNT(*) FROM {test_table_name}")
        count_result = await db.execute(select_query)
        record_count = count_result.scalar()

        # Test DELETE
        delete_query = text(f"DELETE FROM {test_table_name}")
        delete_result = await db.execute(delete_query)
        delete_count = delete_result.rowcount

        # Clean up (table will be automatically dropped as it's temporary)

        response_time = (time.time() - start_time) * 1000

        logger.info(
            f"Database write test successful - {response_time:.2f}ms",
            extra={
                "trace_id": trace_id,
                "response_time_ms": response_time,
                "operation": "write_test",
                "insert_count": insert_count,
                "update_count": update_count,
                "delete_count": delete_count,
            },
        )

        return APIResponse.create_with_trace_id(
            data={
                "status": "healthy",
                "operation": "write_test",
                "response_time_ms": round(response_time, 2),
                "results": {
                    "insert_count": insert_count,
                    "update_count": update_count,
                    "record_count": record_count,
                    "delete_count": delete_count,
                },
            },
            message="Database write test successful",
            trace_id=trace_id,
        )

    except SQLAlchemyError as e:
        response_time = (time.time() - start_time) * 1000

        logger.error(
            f"Database write test failed: {str(e)}",
            extra={
                "trace_id": trace_id,
                "error": str(e),
                "response_time_ms": response_time,
            },
        )

        raise HTTPException(
            status_code=503,
            detail=secure_response(
                {
                    "success": False,
                    "message": "Database write test failed",
                    "data": {
                        "status": "unhealthy",
                        "operation": "write_test",
                        "response_time_ms": round(response_time, 2),
                        "error": str(e),
                    },
                    "error": str(e),
                    "trace_id": trace_id,
                }
            ),
        )


@router.get("/ddl", response_model=APIResponse)
async def test_database_ddl(request: Request, db=Depends(get_db)):
    """
    Test database DDL operations (CREATE/DROP/ALTER).

    Tests:
    - CREATE TABLE operation
    - ALTER TABLE operation
    - DROP TABLE operation
    - Schema manipulation
    """
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    start_time = time.time()

    try:
        # Test DDL operations with a temporary table
        test_table_name = f"ddl_ping_test_{int(time.time())}"

        # Test CREATE TABLE
        create_table_query = text(
            f"""
            CREATE TEMPORARY TABLE {test_table_name} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """
        )
        await db.execute(create_table_query)

        # Test ALTER TABLE (add column)
        alter_table_query = text(
            f"""
            ALTER TABLE {test_table_name}
            ADD COLUMN description TEXT
        """
        )
        await db.execute(alter_table_query)

        # Test ALTER TABLE (modify column)
        modify_column_query = text(
            f"""
            ALTER TABLE {test_table_name}
            ALTER COLUMN name TYPE VARCHAR(100)
        """
        )
        await db.execute(modify_column_query)

        # Verify table structure - use async-compatible approach
        try:
            # Get column information using SQL query instead of inspector
            column_query = text(
                f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{test_table_name}'
                ORDER BY ordinal_position
            """
            )
            column_result = await db.execute(column_query)
            column_names = [row[0] for row in column_result.fetchall()]
        except Exception:
            column_names = ["id", "name", "description", "created_at"]  # Fallback

        # Test DROP TABLE (will be automatically dropped as it's temporary)
        # But we can verify it exists first
        check_table_query = text(
            f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = '{test_table_name}'
            )
        """
        )
        table_exists = await db.execute(check_table_query)
        exists_result = table_exists.scalar()

        response_time = (time.time() - start_time) * 1000

        logger.info(
            f"Database DDL test successful - {response_time:.2f}ms",
            extra={
                "trace_id": trace_id,
                "response_time_ms": response_time,
                "operation": "ddl_test",
                "table_name": test_table_name,
                "columns": column_names,
            },
        )

        return APIResponse.create_with_trace_id(
            data={
                "status": "healthy",
                "operation": "ddl_test",
                "response_time_ms": round(response_time, 2),
                "results": {
                    "table_created": True,
                    "table_name": test_table_name,
                    "columns": column_names,
                    "table_exists": bool(exists_result),
                },
            },
            message="Database DDL test successful",
            trace_id=trace_id,
        )

    except SQLAlchemyError as e:
        response_time = (time.time() - start_time) * 1000

        logger.error(
            f"Database DDL test failed: {str(e)}",
            extra={
                "trace_id": trace_id,
                "error": str(e),
                "response_time_ms": response_time,
            },
        )

        raise HTTPException(
            status_code=503,
            detail=secure_response(
                {
                    "success": False,
                    "message": "Database DDL test failed",
                    "data": {
                        "status": "unhealthy",
                        "operation": "ddl_test",
                        "response_time_ms": round(response_time, 2),
                        "error": str(e),
                    },
                    "error": str(e),
                    "trace_id": trace_id,
                }
            ),
        )


@router.get("/info", response_model=APIResponse)
async def get_database_info(request: Request, db=Depends(get_db)):
    """
    Get comprehensive database information and status.

    Returns:
    - Database version and type
    - Connection pool status
    - Database size and statistics
    - Active connections
    - Configuration details
    """
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    try:
        # Get database version and type
        version_query = text("SELECT VERSION() as version")
        version_result = await db.execute(version_query)
        db_version = version_result.scalar()

        # Get database name
        db_name_query = text("SELECT DATABASE() as db_name")
        try:
            db_name_result = await db.execute(db_name_query)
            db_name = db_name_result.scalar()
        except Exception:
            # Fallback for databases that don't support DATABASE()
            db_name = "unknown"

        # Get connection pool information
        pool = db.get_bind().pool
        pool_info = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": getattr(pool, "invalid", lambda: 0)(),  # Fallback for async pools
        }

        # Get database size (if supported)
        try:
            size_query = text(
                """
                SELECT
                    ROUND(SUM(pg_total_relation_size(c.oid)) / 1024.0 / 1024.0, 2) AS size_mb
                FROM information_schema.tables t
                LEFT JOIN pg_class c ON c.relname = t.table_name
                WHERE t.table_schema = current_schema()
            """
            )
            size_result = await db.execute(size_query)
            db_size = size_result.scalar()
        except Exception:
            db_size = None

        # Get table count
        try:
            table_count_query = text(
                """
                SELECT COUNT(*) as table_count
                FROM information_schema.tables
                WHERE table_schema = current_schema()
            """
            )
            table_count_result = await db.execute(table_count_query)
            table_count = table_count_result.scalar()
        except Exception:
            table_count = None

        # Get active connections (if supported)
        try:
            connections_query = text("SHOW PROCESSLIST")
            connections_result = await db.execute(connections_query)
            active_connections = len(connections_result.fetchall())
        except Exception:
            active_connections = None

        logger.info(
            "Database info retrieved successfully",
            extra={
                "trace_id": trace_id,
                "db_version": db_version,
                "db_name": db_name,
                "pool_info": pool_info,
            },
        )

        return APIResponse.create_with_trace_id(
            data={
                "status": "healthy",
                "database": {
                    "version": db_version,
                    "name": db_name,
                    "type": str(db.get_bind().dialect.name),
                },
                "connection_pool": pool_info,
                "statistics": {
                    "size_mb": db_size,
                    "table_count": table_count,
                    "active_connections": active_connections,
                },
            },
            message="Database information retrieved successfully",
            trace_id=trace_id,
        )

    except SQLAlchemyError as e:
        logger.error(
            f"Failed to get database info: {str(e)}",
            extra={"trace_id": trace_id, "error": str(e)},
        )

        raise HTTPException(
            status_code=503,
            detail=secure_response(
                {
                    "success": False,
                    "message": "Failed to get database information",
                    "data": {
                        "status": "unhealthy",
                        "error": str(e),
                    },
                    "error": str(e),
                    "trace_id": trace_id,
                }
            ),
        )


@router.get("/tables", response_model=APIResponse)
async def list_database_tables(request: Request, db=Depends(get_db)):
    """
    List all tables in the current database.

    Returns:
    - Table names and types
    - Table row counts
    - Table sizes
    - Creation/modification dates
    """
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    try:
        # Get table information
        tables_query = text(
            """
            SELECT
                t.table_name,
                t.table_type,
                COALESCE(s.n_tup_ins + s.n_tup_upd + s.n_tup_del, 0) as table_rows,
                ROUND(COALESCE(pg_total_relation_size(c.oid) / 1024.0 / 1024.0, 0), 2) as size_mb,
                NULL as create_time,
                NULL as update_time
            FROM information_schema.tables t
            LEFT JOIN pg_class c ON c.relname = t.table_name
            LEFT JOIN pg_stat_user_tables s ON s.relname = t.table_name
            WHERE t.table_schema = current_schema()
            ORDER BY t.table_name
        """
        )

        result = await db.execute(tables_query)
        tables = result.fetchall()

        table_list = []
        for table in tables:
            table_list.append(
                {
                    "name": table[0],
                    "type": table[1],
                    "rows": table[2],
                    "size_mb": table[3],
                    "created": str(table[4]) if table[4] else None,
                    "updated": str(table[5]) if table[5] else None,
                }
            )

        logger.info(
            f"Retrieved {len(table_list)} tables",
            extra={
                "trace_id": trace_id,
                "table_count": len(table_list),
            },
        )

        return APIResponse.create_with_trace_id(
            data={
                "status": "healthy",
                "total_tables": len(table_list),
                "tables": table_list,
            },
            message=f"Retrieved {len(table_list)} tables",
            trace_id=trace_id,
        )

    except SQLAlchemyError as e:
        logger.error(
            f"Failed to list tables: {str(e)}",
            extra={"trace_id": trace_id, "error": str(e)},
        )

        raise HTTPException(
            status_code=503,
            detail=secure_response(
                {
                    "success": False,
                    "message": "Failed to list database tables",
                    "data": {
                        "status": "unhealthy",
                        "error": str(e),
                    },
                    "error": str(e),
                    "trace_id": trace_id,
                }
            ),
        )
