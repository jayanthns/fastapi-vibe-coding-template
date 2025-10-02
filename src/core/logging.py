"""
Comprehensive logging system for the application.
Handles configuration, setup, utilities, and formatters in one place.
"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import Request


class TraceIDFormatter(logging.Formatter):
    """Custom formatter that includes trace_id in log messages."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        if fmt is None:
            fmt = (
                "%(asctime)s | %(levelname)-8s | %(trace_id)s | %(name)s | %(message)s"
            )
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        # Ensure trace_id is present, default to 'no-trace-id' if not set
        if not hasattr(record, "trace_id"):
            record.trace_id = "no-trace-id"
        return super().format(record)


class RequestLogger:
    """
    Request-scoped logger that automatically includes trace_id in all log messages.
    Similar to Django's request-level logging pattern.
    """

    def __init__(self, trace_id: str, logger_name: str = "app"):
        self.trace_id = trace_id
        self.logger = logging.getLogger(logger_name)

        # Create a custom adapter that adds trace_id to all log records
        self._adapter = logging.LoggerAdapter(self.logger, {"trace_id": trace_id})

    def debug(self, msg: str, *args, **kwargs):
        self._adapter.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._adapter.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._adapter.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._adapter.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._adapter.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        self._adapter.exception(msg, *args, **kwargs)


class LoggingConfig:
    """Configuration class for application logging."""

    def __init__(self):
        self.logs_dir = Path("tmp/logs")
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        # Log file paths
        self.log_files = {
            "app": self.logs_dir / f"app-{self.current_date}.log",
            "sqlalchemy": self.logs_dir / f"sqlalchemy-{self.current_date}.log",
        }

        # Log rotation settings
        self.max_bytes = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5

    def setup_logging(self) -> None:
        """
        Setup application-wide logging configuration with both console and file output.
        Call this once during application startup.
        """
        # Create logs directory
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Setup file logging
        self._setup_file_logging()

        # Setup console logging
        self._setup_console_logging()

        # Log startup message
        app_logger = logging.getLogger("app")
        app_logger.info(
            f"Logging initialized - Console and file: {self.log_files['app']}"
        )

    def _setup_file_logging(self) -> None:
        """Setup file-based logging with rotation."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(trace_id)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(trace_id)s | %(name)s | %(message)s"
        )

        # Setup app logger with rotation
        app_logger = logging.getLogger("app")
        app_logger.setLevel(logging.INFO)

        # App log file handler with rotation
        app_file_handler = logging.handlers.RotatingFileHandler(
            self.log_files["app"],
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
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
            self.log_files["sqlalchemy"],
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        sql_file_handler.setLevel(logging.INFO)
        sql_file_handler.setFormatter(simple_formatter)
        sql_file_handler.addFilter(lambda record: hasattr(record, "trace_id"))

        sqlalchemy_logger.addHandler(sql_file_handler)
        sqlalchemy_logger.propagate = False

    def _setup_console_logging(self) -> None:
        """Setup console logging."""
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Set custom formatter for console
        formatter = TraceIDFormatter()
        console_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)

        # Configure app logger
        app_logger = logging.getLogger("app")
        app_logger.setLevel(logging.INFO)
        app_logger.propagate = False
        app_logger.addHandler(console_handler)

    def get_log_file_path(self, log_type: str = "app") -> Path | None:
        """
        Get the current log file path for a specific log type.

        Args:
            log_type: Type of log file ('app', 'sqlalchemy')

        Returns:
            Path to the current log file
        """
        return self.log_files.get(log_type)


# Global logging configuration instance
logging_config = LoggingConfig()


# Utility functions
def get_logger_for_trace_id(trace_id: str, logger_name: str = "app") -> RequestLogger:
    """
    Create a logger for a specific trace_id (useful for background/async tasks).

    Usage:
        from src.core.logging import get_logger_for_trace_id

        async def background_task(trace_id: str):
            logger = get_logger_for_trace_id(trace_id)
            logger.info("Doing background work")
    """
    return RequestLogger(trace_id, logger_name)


def get_logger(request: Request) -> RequestLogger:
    """
    Shortcut function to get request logger.

    Usage:
        from src.core.logging import get_logger

        @router.get("/")
        async def endpoint(request: Request):
            logger = get_logger(request)
            logger.info("Processing request")
    """
    from src.middleware.trace import get_trace_id
    trace_id = get_trace_id(request)
    return RequestLogger(trace_id, "app.request")


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
    request_logger = RequestLogger(trace_id, "app.access")
    request_logger.info(f"ACCESS: {method} {path} - {status_code} - {processing_time:.4f}s")


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
    request_logger = RequestLogger(trace_id, "app.error")
    request_logger.error(f"ERROR: {error_message}")


def setup_logging() -> None:
    """
    Setup application-wide logging configuration.
    This is the main entry point for logging setup.
    """
    logging_config.setup_logging()
