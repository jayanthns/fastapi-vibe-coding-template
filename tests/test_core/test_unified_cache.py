import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.core.cache.unified_cache import UnifiedCacheService


@pytest.fixture
def unified_cache():
    return UnifiedCacheService()


@pytest.fixture
def mock_redis_service():
    with patch("src.core.cache.unified_cache.redis_cache_service") as mock:
        # Configure async methods
        mock.get = AsyncMock()
        mock.set = AsyncMock()
        mock.delete = AsyncMock()
        mock.exists = AsyncMock()
        mock.expire = AsyncMock()
        mock.ttl = AsyncMock()
        mock.keys = AsyncMock()
        mock.info = AsyncMock(return_value={})
        mock.ping = AsyncMock()
        mock.clear = AsyncMock()
        mock.clear_pattern = AsyncMock()
        yield mock


@pytest.fixture
def mock_memory_service():
    with patch("src.core.cache.unified_cache.memory_cache_service") as mock:
        # Configure async methods
        mock.get = AsyncMock()
        mock.set = AsyncMock()
        mock.delete = AsyncMock()
        mock.exists = AsyncMock()
        mock.expire = AsyncMock()
        mock.ttl = AsyncMock()
        mock.keys = AsyncMock()
        mock.info = AsyncMock(return_value={})
        mock.ping = AsyncMock()
        mock.clear = AsyncMock()
        mock.clear_pattern = AsyncMock()
        yield mock


@pytest.mark.asyncio
async def test_unified_cache_redis_selection(
    unified_cache, mock_redis_service, mock_memory_service
):
    with patch("src.core.cache.unified_cache.settings.use_redis", True):
        # Force re-evaluation
        unified_cache._service = None
        unified_cache._service_type = None

        await unified_cache.get("key")
        mock_redis_service.get.assert_called_with("key")
        mock_memory_service.get.assert_not_called()
        assert unified_cache.service_type == "redis"
        assert unified_cache.is_redis is True
        assert unified_cache.is_memory is False


@pytest.mark.asyncio
async def test_unified_cache_memory_selection(
    unified_cache, mock_redis_service, mock_memory_service
):
    with patch("src.core.cache.unified_cache.settings.use_redis", False):
        # Force re-evaluation
        unified_cache._service = None
        unified_cache._service_type = None

        await unified_cache.get("key")
        mock_memory_service.get.assert_called_with("key")
        mock_redis_service.get.assert_not_called()
        assert unified_cache.service_type == "memory"
        assert unified_cache.is_redis is False
        assert unified_cache.is_memory is True


@pytest.mark.asyncio
async def test_unified_cache_switching(
    unified_cache, mock_redis_service, mock_memory_service
):
    # Start with Redis
    with patch("src.core.cache.unified_cache.settings.use_redis", True):
        unified_cache._service = None
        unified_cache._service_type = None
        await unified_cache.get("key1")
        mock_redis_service.get.assert_called_with("key1")

    # Switch to Memory
    with patch("src.core.cache.unified_cache.settings.use_redis", False):
        await unified_cache.get("key2")
        mock_memory_service.get.assert_called_with("key2")


@pytest.mark.asyncio
async def test_unified_cache_methods_delegation(unified_cache, mock_redis_service):
    with patch("src.core.cache.unified_cache.settings.use_redis", True):
        unified_cache._service = None
        unified_cache._service_type = None

        # Async methods
        await unified_cache.ping()
        mock_redis_service.ping.assert_called_once()

        await unified_cache.set("k", "v", 60)
        mock_redis_service.set.assert_called_with("k", "v", 60)

        await unified_cache.delete("k")
        mock_redis_service.delete.assert_called_with("k")

        await unified_cache.exists("k")
        mock_redis_service.exists.assert_called_with("k")

        await unified_cache.expire("k", 60)
        mock_redis_service.expire.assert_called_with("k", 60)

        await unified_cache.ttl("k")
        mock_redis_service.ttl.assert_called_with("k")

        await unified_cache.keys("*")
        mock_redis_service.keys.assert_called_with("*")

        await unified_cache.info()
        mock_redis_service.info.assert_called_once()

        await unified_cache.clear()
        mock_redis_service.clear.assert_called_once()

        await unified_cache.clear_pattern("p*")
        mock_redis_service.clear_pattern.assert_called_with("p*")


def test_unified_cache_sync_methods_delegation(unified_cache, mock_redis_service):
    with patch("src.core.cache.unified_cache.settings.use_redis", True):
        unified_cache._service = None
        unified_cache._service_type = None

        # Sync methods
        unified_cache.ping_sync()
        mock_redis_service.ping_sync.assert_called_once()

        unified_cache.get_sync("k")
        mock_redis_service.get_sync.assert_called_with("k")

        unified_cache.set_sync("k", "v", 60)
        mock_redis_service.set_sync.assert_called_with("k", "v", 60)

        unified_cache.delete_sync("k")
        mock_redis_service.delete_sync.assert_called_with("k")

        unified_cache.exists_sync("k")
        mock_redis_service.exists_sync.assert_called_with("k")

        unified_cache.expire_sync("k", 60)
        mock_redis_service.expire_sync.assert_called_with("k", 60)

        unified_cache.ttl_sync("k")
        mock_redis_service.ttl_sync.assert_called_with("k")

        unified_cache.keys_sync("*")
        mock_redis_service.keys_sync.assert_called_with("*")

        unified_cache.info_sync()
        mock_redis_service.info_sync.assert_called_once()

        unified_cache.clear_sync()
        mock_redis_service.clear_sync.assert_called_once()

        unified_cache.clear_pattern_sync("p*")
        mock_redis_service.clear_pattern_sync.assert_called_with("p*")
