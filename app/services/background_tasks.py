"""
Example of how to use trace_id-aware logging in background/async tasks.
"""

import asyncio

from app.core.logging import get_logger_for_trace_id


async def process_article_async(article_id: int, trace_id: str) -> None:
    """
    Example background task that uses trace_id-aware logging.

    Usage:
        from app.services.background_tasks import process_article_async

        # In your endpoint:
        @router.post("/articles/{article_id}/process")
        async def process_article(article_id: int, request: Request):
            trace_id = get_trace_id(request)

            # Start background task with trace_id
            asyncio.create_task(process_article_async(article_id, trace_id))

            return {"message": "Processing started"}
    """
    # Create logger with the request's trace_id
    logger = get_logger_for_trace_id(trace_id, "app.background")

    logger.info(f"Starting background processing for article {article_id}")

    try:
        # Simulate some async work
        await asyncio.sleep(2)
        logger.info(f"Processing step 1 completed for article {article_id}")

        await asyncio.sleep(1)
        logger.info(f"Processing step 2 completed for article {article_id}")

        # Simulate potential error
        # raise Exception("Simulated error")

        logger.info(f"Background processing completed for article {article_id}")

    except Exception as e:
        logger.error(f"Background processing failed for article {article_id}: {str(e)}")
        raise


async def send_notification_async(user_id: int, message: str, trace_id: str) -> None:
    """
    Another example of background task with trace_id logging.
    """
    logger = get_logger_for_trace_id(trace_id, "app.notifications")

    logger.info(f"Sending notification to user {user_id}: {message}")

    try:
        # Simulate sending notification
        await asyncio.sleep(0.5)
        logger.info(f"Notification sent successfully to user {user_id}")

    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
        raise


# Example of how to use in an endpoint:
"""
from fastapi import BackgroundTasks
from app.middleware.trace import get_trace_id

@router.post("/articles/{article_id}/process")
async def process_article(
    article_id: int,
    request: Request,
    background_tasks: BackgroundTasks
):
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Starting background processing for article {article_id}")

    # Add background task with trace_id
    background_tasks.add_task(process_article_async, article_id, trace_id)

    return {"message": "Processing started", "trace_id": trace_id}
"""
