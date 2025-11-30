import pytest
from unittest.mock import patch
from src.apps.background_jobs.tasks import test_background_task, test_failing_task


class TestBackgroundJobsTasks:
    def test_background_task_success(self):
        with patch("time.sleep") as mock_sleep:
            result = test_background_task(duration=5)
            mock_sleep.assert_called_once_with(5)
            assert result == {"status": "success", "duration": 5}

    def test_failing_task_raises_error(self):
        with pytest.raises(ValueError, match="This is a simulated failure"):
            test_failing_task()
