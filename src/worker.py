import dramatiq
from dramatiq.brokers.redis import RedisBroker
from src.core.config import settings

# Configure Redis Broker
redis_broker = RedisBroker(url=settings.redis_url)
dramatiq.set_broker(redis_broker)

# Import tasks here to ensure they are registered
# from src.apps.some_app import tasks
