import dramatiq

print("DEBUG: src/worker.py imported")
from dramatiq.brokers.redis import RedisBroker

from src.apps.background_jobs.middleware import JobTrackingMiddleware
from src.core.config import settings
from src.core.logging import setup_logging

# Setup logging with consistent format
setup_logging()

# Configure Redis Broker
redis_broker = RedisBroker(url=settings.redis_url)
redis_broker.add_middleware(JobTrackingMiddleware())
dramatiq.set_broker(redis_broker)

# Import tasks here to ensure they are registered
from src.apps.audit import tasks as audit_tasks  # noqa: F401
from src.apps.background_jobs import tasks as bg_tasks  # noqa: F401
