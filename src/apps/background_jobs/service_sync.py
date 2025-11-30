from src.apps.background_jobs.models import JobStatus
from src.apps.background_jobs.repository_sync import JobRepositorySync
from src.db.session_sync import SessionLocalSync


class JobServiceSync:
    @staticmethod
    def update_status_by_message_id(
        message_id: str,
        status: JobStatus,
        result: any = None,
        error: str = None,
        traceback: str = None,
    ):
        """
        Used by Middleware to update job status synchronously.
        Creates a new sync session.
        """
        with SessionLocalSync() as session:
            repo = JobRepositorySync(session)
            job = repo.get_by_message_id(message_id)
            if job:
                update_data = {"status": status}
                if result is not None:
                    update_data["result"] = result
                if error is not None:
                    update_data["error"] = error
                if traceback is not None:
                    update_data["traceback"] = traceback

                repo.update(job.id, **update_data)
