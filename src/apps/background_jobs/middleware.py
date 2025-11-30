import asyncio
import traceback

import dramatiq

from src.apps.background_jobs.models import JobStatus
from src.apps.background_jobs.service import JobService


class JobTrackingMiddleware(dramatiq.Middleware):
    def before_process_message(self, broker, message):
        try:
            asyncio.run(
                JobService.update_status_by_message_id(
                    message_id=message.message_id, status=JobStatus.RUNNING
                )
            )
        except Exception as e:
            print(f"Error updating job status to RUNNING: {e}")

    def after_process_message(self, broker, message, *, result=None, exception=None):
        try:
            if exception:
                error_msg = str(exception)
                tb = "".join(traceback.format_tb(exception.__traceback__))
                asyncio.run(
                    JobService.update_status_by_message_id(
                        message_id=message.message_id,
                        status=JobStatus.FAILED,
                        error=error_msg,
                        traceback=tb,
                    )
                )
            else:
                asyncio.run(
                    JobService.update_status_by_message_id(
                        message_id=message.message_id,
                        status=JobStatus.COMPLETED,
                        result=result,
                    )
                )
        except Exception as e:
            print(f"Error updating job status to COMPLETED/FAILED: {e}")

    def after_skip_message(self, broker, message):
        # Handle skipped messages (e.g. retries exhausted or other reasons)
        # For now, we might not track this explicitly or mark as FAILED?
        pass
