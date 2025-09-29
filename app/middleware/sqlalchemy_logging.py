"""
SQLAlchemy logging integration with trace_id system.
Configures SQLAlchemy to use our trace_id-aware logging.
"""

import logging

from sqlalchemy import event
from sqlalchemy.engine import Engine


class SQLAlchemyTraceIDHandler(logging.Handler):
    """
    Custom logging handler that adds trace_id to SQLAlchemy log records.
    """

    def __init__(self, trace_id: str):
        super().__init__()
        self.trace_id = trace_id

    def emit(self, record: logging.LogRecord) -> None:
        # Add trace_id to the log record
        record.trace_id = self.trace_id
        # Use the app logger to emit the record
        logger = logging.getLogger("app.sqlalchemy")
        logger.handle(record)


def setup_sqlalchemy_logging(trace_id: str) -> None:
    """
    Setup SQLAlchemy logging with trace_id (only in development environment).

    Args:
        trace_id: The trace ID to include in SQLAlchemy logs
    """
    from app.core.config import settings

    # Only enable SQL logging in development environment
    if settings.environment != "development":
        return

    # Get SQLAlchemy engine logger
    engine_logger = logging.getLogger("sqlalchemy.engine.Engine")

    # Remove existing handlers to avoid duplicate logs
    engine_logger.handlers.clear()

    # Add our custom handler with trace_id
    handler = SQLAlchemyTraceIDHandler(trace_id)
    handler.setLevel(logging.INFO)

    # Set formatter
    from app.middleware.logging import TraceIDFormatter

    formatter = TraceIDFormatter()
    handler.setFormatter(formatter)

    # Add handler to engine logger
    engine_logger.addHandler(handler)
    engine_logger.setLevel(logging.INFO)
    engine_logger.propagate = False


def clear_sqlalchemy_logging() -> None:
    """
    Clear SQLAlchemy logging handlers.
    """
    engine_logger = logging.getLogger("sqlalchemy.engine.Engine")
    engine_logger.handlers.clear()
    engine_logger.propagate = True


# Alternative approach: Use SQLAlchemy events to log with trace_id
def setup_sqlalchemy_event_logging(engine: Engine, trace_id: str) -> None:
    """
    Setup SQLAlchemy event-based logging with trace_id (only in development environment).
    This approach uses SQLAlchemy events instead of logging handlers.
    """
    from app.core.config import settings

    # Only enable SQL logging in development environment
    if settings.environment != "development":
        return

    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        """Log SQL statements before execution."""
        logger = logging.getLogger("app.sqlalchemy")
        # Create a custom log record with trace_id
        record = logging.LogRecord(
            name="app.sqlalchemy",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"SQL: {statement[:100]}{'...' if len(statement) > 100 else ''}",
            args=(),
            exc_info=None,
        )
        record.trace_id = trace_id
        logger.handle(record)

    @event.listens_for(engine, "after_cursor_execute")
    def receive_after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        """Log SQL execution completion."""
        logger = logging.getLogger("app.sqlalchemy")
        record = logging.LogRecord(
            name="app.sqlalchemy",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="SQL execution completed",
            args=(),
            exc_info=None,
        )
        record.trace_id = trace_id
        logger.handle(record)


def get_sqlalchemy_logger(trace_id: str):
    """
    Get a SQLAlchemy logger with trace_id.

    Args:
        trace_id: The trace ID to include in logs

    Returns:
        Logger instance with trace_id
    """
    logger = logging.getLogger("app.sqlalchemy")

    # Create a custom adapter that adds trace_id
    class TraceIDAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return msg, {
                **kwargs,
                "extra": {
                    **kwargs.get("extra", {}),
                    "trace_id": self.extra["trace_id"],
                },
            }

    return TraceIDAdapter(logger, {"trace_id": trace_id})
