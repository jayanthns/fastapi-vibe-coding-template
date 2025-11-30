"""
Background task management and cleanup.
Handles periodic cleanup of old jobs and system maintenance.
"""

import asyncio

from src.apps.background_jobs.service import background_job_service
from src.core.logging import get_logger_for_trace_id


class BackgroundTaskManager:
    """Manages background tasks and cleanup operations."""

    def __init__(self):
        self._cleanup_task: asyncio.Task | None = None  # type: ignore
        self._running = False

    async def start(self):
        """Start background task manager."""
        if self._running:
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger = get_logger_for_trace_id("system", "src.background_tasks")
        logger.info("Background task manager started")

    async def stop(self):
        """Stop background task manager."""
        if not self._running:
            return

        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger = get_logger_for_trace_id("system", "src.background_tasks")
        logger.info("Background task manager stopped")

    async def _cleanup_loop(self):
        """Main cleanup loop that runs every hour."""
        logger = get_logger_for_trace_id("system", "src.background_tasks")

        while self._running:
            try:
                # Wait for 1 hour
                await asyncio.sleep(3600)

                if self._running:
                    logger.info("Starting background job cleanup")
                    await background_job_service.cleanup_old_jobs(hours=24)
                    logger.info("Background job cleanup completed")

            except asyncio.CancelledError:
                logger.info("Background cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background cleanup: {str(e)}")
                # Continue running even if cleanup fails
                await asyncio.sleep(300)  # Wait 5 minutes before retrying


# Global instance
background_task_manager = BackgroundTaskManager()
