"""
Request-level logging middleware and utilities.
Provides trace_id-aware logging throughout the request lifecycle.
"""

import logging
import sys
from typing import Optional
from uuid import uuid4

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
        # Add trace_id to the log record if not present
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

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message with trace_id."""
        self._adapter.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message with trace_id."""
        self._adapter.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message with trace_id."""
        self._adapter.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message with trace_id."""
        self._adapter.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message with trace_id."""
        self._adapter.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback and trace_id."""
        self._adapter.exception(message, *args, **kwargs)

    def log(self, level: int, message: str, *args, **kwargs) -> None:
        """Log message at specified level with trace_id."""
        self._adapter.log(level, message, *args, **kwargs)


def get_request_logger(request: Request, logger_name: str = "app") -> RequestLogger:
    """
    Get the request-scoped logger with trace_id.

    Usage:
        from app.middleware.logging import get_request_logger

        @router.get("/")
        async def endpoint(request: Request):
            logger = get_request_logger(request)
            logger.info("Processing request")
            return {"status": "ok"}
    """
    trace_id = getattr(request.state, "trace_id", str(uuid4()))
    return RequestLogger(trace_id, logger_name)


def get_logger_for_trace_id(trace_id: str, logger_name: str = "app") -> RequestLogger:
    """
    Create a logger for a specific trace_id (useful for background/async tasks).

    Usage:
        from app.middleware.logging import get_logger_for_trace_id

        async def background_task(trace_id: str):
            logger = get_logger_for_trace_id(trace_id)
            logger.info("Starting background task")
    """
    return RequestLogger(trace_id, logger_name)


def setup_logging() -> None:
    """
    Setup application-wide logging configuration.
    Call this once during application startup.
    """
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Set custom formatter
    formatter = TraceIDFormatter()
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Configure app logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    app_logger.propagate = False
    app_logger.addHandler(console_handler)


# Convenience function for getting logger from request
def get_logger(request: Request) -> RequestLogger:
    """
    Shortcut function to get request logger.

    Usage:
        from app.middleware.logging import get_logger

        @router.get("/")
        async def endpoint(request: Request):
            logger = get_logger(request)
            logger.info("Hello world")
    """
    return get_request_logger(request)
