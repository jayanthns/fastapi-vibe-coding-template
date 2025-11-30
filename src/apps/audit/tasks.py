"""Dramatiq tasks for audit logging."""

import logging
import dramatiq
from src.apps.audit.repository_sync import AuditLogRepositorySync
from src.apps.audit.schemas import AuditLogCreate
from src.db.session_sync import SessionLocalSync

logger = logging.getLogger(__name__)


@dramatiq.actor
def write_audit_log(payload: dict):
    try:
        # Extract trace_id from payload
        trace_id = payload.get("trace_id")

        audit_data = AuditLogCreate(
            action=payload["action"],
            target_model=payload["target_model"],
            target_object_id=payload["target_object_id"],
            actor_id=payload.get("actor_id"),
            actor_email=payload.get("actor_email"),
            changes=payload.get("changes", {}),
            ip_address=payload.get("ip_address"),
            user_agent=payload.get("user_agent"),
            trace_id=trace_id,
        )

        with SessionLocalSync() as session:
            repo = AuditLogRepositorySync(session)
            audit_log = repo.create(audit_data)
            logger.info(
                f"Audit log created: {audit_log.action} on {audit_log.target_model} "
                f"({audit_log.target_object_id}) [Trace ID: {trace_id}]"
            )
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        raise e
