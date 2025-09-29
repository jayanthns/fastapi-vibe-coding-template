"""
Advanced file logging configuration with rotation and different log levels.
"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_file_logging() -> None:
    """
    Setup advanced file logging with rotation and different log levels.
    """
    # Create logs directory
    logs_dir = Path("tmp/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Get current date for log file naming
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Setup simplified log files - just 2 files for clarity
    log_files = {
        "app": logs_dir / f"app-{current_date}.log",  # All application logs
        "sqlalchemy": logs_dir
        / f"sqlalchemy-{current_date}.log",  # Database queries (dev only)
    }

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(trace_id)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(trace_id)s | %(name)s | %(message)s"
    )

    # Setup app logger with rotation - handles ALL application logs
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    # App log file handler with rotation (10MB max, keep 5 files)
    app_file_handler = logging.handlers.RotatingFileHandler(
        log_files["app"],
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(detailed_formatter)
    app_file_handler.addFilter(lambda record: hasattr(record, "trace_id"))

    app_logger.addHandler(app_file_handler)
    app_logger.propagate = False

    # Setup SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("app.sqlalchemy")
    sqlalchemy_logger.setLevel(logging.INFO)

    # SQLAlchemy log file handler
    sql_file_handler = logging.handlers.RotatingFileHandler(
        log_files["sqlalchemy"],
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    sql_file_handler.setLevel(logging.INFO)
    sql_file_handler.setFormatter(simple_formatter)
    sql_file_handler.addFilter(lambda record: hasattr(record, "trace_id"))

    sqlalchemy_logger.addHandler(sql_file_handler)
    sqlalchemy_logger.propagate = False


def get_log_file_path(log_type: str = "app") -> Optional[Path]:
    """
    Get the current log file path for a specific log type.

    Args:
        log_type: Type of log file ('app', 'sqlalchemy', 'error', 'access')

    Returns:
        Path to the current log file
    """
    logs_dir = Path("tmp/logs")
    current_date = datetime.now().strftime("%Y-%m-%d")

    log_files = {
        "app": logs_dir / f"app-{current_date}.log",
        "sqlalchemy": logs_dir / f"sqlalchemy-{current_date}.log",
    }

    return log_files.get(log_type)


def log_request_access(
    trace_id: str, method: str, path: str, status_code: int, processing_time: float
) -> None:
    """
    Log request access information to the main app log.

    Args:
        trace_id: Request trace ID
        method: HTTP method
        path: Request path
        status_code: Response status code
        processing_time: Request processing time in seconds
    """
    # Use the RequestLogger to get proper function context
    from app.middleware.logging import RequestLogger

    request_logger = RequestLogger(trace_id, "app.access")
    request_logger.info(
        f"ACCESS: {method} {path} - {status_code} - {processing_time:.4f}s"
    )


def log_error(
    trace_id: str, error_message: str, exception: Optional[Exception] = None
) -> None:
    """
    Log error information to the main app log.

    Args:
        trace_id: Request trace ID
        error_message: Error message
        exception: Optional exception object
    """
    # Use the RequestLogger to get proper function context
    from app.middleware.logging import RequestLogger

    request_logger = RequestLogger(trace_id, "app.error")
    request_logger.error(f"ERROR: {error_message}")
