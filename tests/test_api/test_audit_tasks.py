from unittest.mock import MagicMock, patch

import pytest

from src.apps.audit.tasks import write_audit_log


class TestAuditTasks:
    def test_write_audit_log_success(self):
        payload = {
            "action": "create",
            "target_model": "user",
            "target_object_id": "user_1",
            "actor_id": "actor_1",
            "actor_email": "actor1@example.com",
            "changes": {"field": "value"},
            "trace_id": "trace_1",
        }

        with patch("src.apps.audit.tasks.SessionLocalSync") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value.__enter__.return_value = mock_session

            with patch("src.apps.audit.tasks.AuditLogRepositorySync") as mock_repo_cls:
                mock_repo = MagicMock()
                mock_repo_cls.return_value = mock_repo
                mock_repo.create.return_value = MagicMock(
                    action="create",
                    target_model="user",
                    target_object_id="user_1",
                )

                # Call the underlying function directly to test logic
                write_audit_log.fn(payload)

                mock_repo.create.assert_called_once()
                args, _ = mock_repo.create.call_args
                assert args[0].action == "create"
                assert args[0].trace_id == "trace_1"

    def test_write_audit_log_failure(self):
        payload = {
            "action": "create",
            # Missing required fields to trigger error
        }

        with pytest.raises(Exception):
            write_audit_log(payload)
