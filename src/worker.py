import dramatiq
from dramatiq.brokers.redis import RedisBroker

from src.apps.background_jobs.middleware import JobTrackingMiddleware
from src.core.config import settings

# Configure Redis Broker
redis_broker = RedisBroker(url=settings.redis_url)
redis_broker.add_middleware(JobTrackingMiddleware())
dramatiq.set_broker(redis_broker)

# Import tasks here to ensure they are registered
from src.apps.background_jobs import tasks  # noqa: F401
