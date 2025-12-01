import json
import pickle
from unittest.mock import AsyncMock, patch

import pytest

from src.core.cache.cache import CacheManager, cache_key, cached, cached_sync


@pytest.fixture
def mock_unified_cache():
    with patch("src.core.cache.cache.unified_cache_service") as mock:
        yield mock


@pytest.mark.asyncio
async def test_cache_manager_get_json(mock_unified_cache):
    data = {"key": "value"}
    mock_unified_cache.get = AsyncMock(return_value=json.dumps(data))

    result = await CacheManager.get("test_key")
    assert result == data


@pytest.mark.asyncio
async def test_cache_manager_get_pickle(mock_unified_cache):
    data = {"key": "value"}
    pickled_data = pickle.dumps(data).decode("latin1")
    mock_unified_cache.get = AsyncMock(return_value=pickled_data)

    # Mock json.loads to fail so it tries pickle
    with patch("json.loads", side_effect=json.JSONDecodeError("msg", "doc", 0)):
        result = await CacheManager.get("test_key")
        assert result == data


@pytest.mark.asyncio
async def test_cache_manager_get_none(mock_unified_cache):
    mock_unified_cache.get = AsyncMock(return_value=None)
    result = await CacheManager.get("test_key", default="default")
    assert result == "default"


@pytest.mark.asyncio
async def test_cache_manager_get_exception(mock_unified_cache):
    mock_unified_cache.get = AsyncMock(side_effect=Exception("Error"))
    result = await CacheManager.get("test_key", default="default")
    assert result == "default"


@pytest.mark.asyncio
async def test_cache_manager_set_json(mock_unified_cache):
    mock_unified_cache.set = AsyncMock(return_value=True)
    data = {"key": "value"}

    result = await CacheManager.set("test_key", data, serialize="json")
    assert result is True
    mock_unified_cache.set.assert_called_with("test_key", json.dumps(data), None)


@pytest.mark.asyncio
async def test_cache_manager_set_pickle(mock_unified_cache):
    mock_unified_cache.set = AsyncMock(return_value=True)
    data = {"key": "value"}

    result = await CacheManager.set("test_key", data, serialize="pickle")
    assert result is True
    # Verify pickle serialization happened
    args = mock_unified_cache.set.call_args[0]
    assert args[0] == "test_key"
    assert pickle.loads(args[1].encode("latin1")) == data


@pytest.mark.asyncio
async def test_cache_manager_set_string(mock_unified_cache):
    mock_unified_cache.set = AsyncMock(return_value=True)
    data = "simple_string"

    result = await CacheManager.set("test_key", data, serialize="string")
    assert result is True
    mock_unified_cache.set.assert_called_with("test_key", "simple_string", None)


@pytest.mark.asyncio
async def test_cache_manager_set_exception(mock_unified_cache):
    mock_unified_cache.set = AsyncMock(side_effect=Exception("Error"))
    result = await CacheManager.set("test_key", "value")
    assert result is False


@pytest.mark.asyncio
async def test_cache_manager_delete(mock_unified_cache):
    mock_unified_cache.delete = AsyncMock(return_value=True)
    result = await CacheManager.delete("test_key")
    assert result is True


@pytest.mark.asyncio
async def test_cache_manager_exists(mock_unified_cache):
    mock_unified_cache.exists = AsyncMock(return_value=True)
    result = await CacheManager.exists("test_key")
    assert result is True


@pytest.mark.asyncio
async def test_cache_manager_expire(mock_unified_cache):
    mock_unified_cache.expire = AsyncMock(return_value=True)
    result = await CacheManager.expire("test_key", 60)
    assert result is True


@pytest.mark.asyncio
async def test_cache_manager_ttl(mock_unified_cache):
    mock_unified_cache.ttl = AsyncMock(return_value=60)
    result = await CacheManager.ttl("test_key")
    assert result == 60


@pytest.mark.asyncio
async def test_cache_manager_clear_pattern(mock_unified_cache):
    mock_unified_cache.keys = AsyncMock(return_value=["key1", "key2"])
    mock_unified_cache.delete = AsyncMock(return_value=True)

    result = await CacheManager.clear_pattern("key*")
    assert result == 2
    assert mock_unified_cache.delete.call_count == 2


@pytest.mark.asyncio
async def test_cache_manager_clear_pattern_no_keys(mock_unified_cache):
    mock_unified_cache.keys = AsyncMock(return_value=[])
    result = await CacheManager.clear_pattern("key*")
    assert result == 0


def test_cache_key_generation():
    assert cache_key("prefix", "arg1", kw="arg2") == "prefix:arg1:kw:arg2"

    class MockObj:
        id = 123

    assert cache_key("prefix", MockObj()) == "prefix:id:123"


@pytest.mark.asyncio
async def test_cached_decorator(mock_unified_cache):
    mock_unified_cache.get = AsyncMock(return_value=None)
    mock_unified_cache.set = AsyncMock(return_value=True)

    @cached(key_prefix="test", expire=60)
    async def test_func(arg):
        return {"data": arg}

    result = await test_func("value")
    assert result == {"data": "value"}
    mock_unified_cache.get.assert_called()
    mock_unified_cache.set.assert_called()


@pytest.mark.asyncio
async def test_cached_decorator_hit(mock_unified_cache):
    data = {"data": "cached"}
    mock_unified_cache.get = AsyncMock(return_value=json.dumps(data))

    @cached(key_prefix="test")
    async def test_func(arg):
        return {"data": arg}

    result = await test_func("value")
    assert result == data
    mock_unified_cache.get.assert_called()
    # set should NOT be called
    # Wait, CacheManager.get calls unified_cache_service.get
    # And CacheManager.get is mocked? No, unified_cache_service is mocked.
    # So CacheManager.get will return the deserialized data.


def test_cached_sync_decorator(mock_unified_cache):
    mock_unified_cache.get_sync.return_value = None
    mock_unified_cache.set_sync.return_value = True

    @cached_sync(key_prefix="test", expire=60)
    def test_func(arg):
        return {"data": arg}

    result = test_func("value")
    assert result == {"data": "value"}
    mock_unified_cache.get_sync.assert_called()
    mock_unified_cache.set_sync.assert_called()


def test_cached_sync_decorator_hit(mock_unified_cache):
    data = {"data": "cached"}
    mock_unified_cache.get_sync.return_value = json.dumps(data)

    @cached_sync(key_prefix="test")
    def test_func(arg):
        return {"data": arg}

    result = test_func("value")
    assert result == data
