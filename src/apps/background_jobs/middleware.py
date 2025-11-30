import traceback

import dramatiq

from src.apps.background_jobs.models import JobStatus
from src.apps.background_jobs.service_sync import JobServiceSync


class JobTrackingMiddleware(dramatiq.Middleware):
    def before_process_message(self, broker, message):
        try:
            # Try to find trace_id in message args/kwargs if possible, or from job DB?
            # Since we don't have easy access to args here without parsing, we might rely on
            # the fact that we saved it to the DB.
            # BUT, for logging purposes, we want it available immediately.
            # Let's check if we can extract it from message options or args.
            # For now, we'll just log what we have.

            # Ideally, we should pass trace_id in message.options or headers.
            # But Dramatiq doesn't have headers in the same way.
            # We can use message.options if we passed it there?
            # JobService.enqueue_job passed it to create_job, but did it pass to actor.send?
            # No.

            # Let's just log the start.
            print(f"Job {message.message_id} started (Task: {message.actor_name})")
            JobServiceSync.update_status_by_message_id(
                message_id=message.message_id, status=JobStatus.RUNNING
            )
        except Exception as e:
            print(f"Error updating job status to RUNNING: {e}")

    def after_process_message(self, broker, message, *, result=None, exception=None):
        try:
            if exception:
                print(f"Job {message.message_id} failed: {exception}")
                error_msg = str(exception)
                tb = "".join(traceback.format_tb(exception.__traceback__))
                JobServiceSync.update_status_by_message_id(
                    message_id=message.message_id,
                    status=JobStatus.FAILED,
                    error=error_msg,
                    traceback=tb,
                )
            else:
                print(f"Job {message.message_id} completed")
                JobServiceSync.update_status_by_message_id(
                    message_id=message.message_id,
                    status=JobStatus.COMPLETED,
                    result=result,
                )
        except Exception as e:
            print(f"Error updating job status to COMPLETED/FAILED: {e}")

    def after_skip_message(self, broker, message):
        # Handle skipped messages (e.g. retries exhausted or other reasons)
        # For now, we might not track this explicitly or mark as FAILED?
        pass
