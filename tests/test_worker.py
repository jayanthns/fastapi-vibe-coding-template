import sys
import pytest
from unittest.mock import MagicMock, patch
import importlib


def test_worker_configuration():
    """Test that the worker module configures the broker correctly."""

    # We need to mock RedisBroker and setup_logging to avoid side effects
    # and to verify they are called.
    with (
        patch("dramatiq.brokers.redis.RedisBroker") as MockBroker,
        patch("src.core.logging.setup_logging") as mock_logging,
        patch(
            "src.apps.background_jobs.middleware.JobTrackingMiddleware"
        ) as MockMiddleware,
        patch("dramatiq.set_broker") as mock_set_broker,
    ):
        # Remove src.worker from sys.modules if it exists to force re-import
        if "src.worker" in sys.modules:
            del sys.modules["src.worker"]

        # Import the module
        import src.worker

        # Verify logging setup
        mock_logging.assert_called()

        # Verify broker setup
        MockBroker.assert_called_once()
        mock_broker_instance = MockBroker.return_value
        MockMiddleware.assert_called_once()
        mock_broker_instance.add_middleware.assert_called()

        # Verify broker was set
        mock_set_broker.assert_called_with(mock_broker_instance)
