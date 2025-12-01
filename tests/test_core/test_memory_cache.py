import asyncio
import time

import pytest

from src.core.cache.memory_cache import MemoryCacheService


@pytest.fixture
def memory_cache():
    return MemoryCacheService()


@pytest.mark.asyncio
async def test_memory_cache_set_get(memory_cache):
    await memory_cache.set("key", "value")
    result = await memory_cache.get("key")
    assert result == "value"


@pytest.mark.asyncio
async def test_memory_cache_get_missing(memory_cache):
    result = await memory_cache.get("missing")
    assert result is None


@pytest.mark.asyncio
async def test_memory_cache_set_get_sync(memory_cache):
    memory_cache.set_sync("key", "value")
    result = memory_cache.get_sync("key")
    assert result == "value"


@pytest.mark.asyncio
async def test_memory_cache_get_missing_sync(memory_cache):
    result = memory_cache.get_sync("missing")
    assert result is None


@pytest.mark.asyncio
async def test_memory_cache_expire(memory_cache):
    await memory_cache.set("key", "value", expire=1)
    assert await memory_cache.get("key") == "value"
    await asyncio.sleep(1.1)
    assert await memory_cache.get("key") is None


@pytest.mark.asyncio
async def test_memory_cache_expire_sync(memory_cache):
    memory_cache.set_sync("key", "value", expire=1)
    assert memory_cache.get_sync("key") == "value"
    time.sleep(1.1)
    assert memory_cache.get_sync("key") is None


@pytest.mark.asyncio
async def test_memory_cache_delete(memory_cache):
    await memory_cache.set("key", "value")
    assert await memory_cache.delete("key") is True
    assert await memory_cache.get("key") is None
    assert await memory_cache.delete("key") is False


@pytest.mark.asyncio
async def test_memory_cache_delete_sync(memory_cache):
    memory_cache.set_sync("key", "value")
    assert memory_cache.delete_sync("key") is True
    assert memory_cache.get_sync("key") is None
    assert memory_cache.delete_sync("key") is False


@pytest.mark.asyncio
async def test_memory_cache_exists(memory_cache):
    await memory_cache.set("key", "value")
    assert await memory_cache.exists("key") is True
    assert await memory_cache.exists("missing") is False


@pytest.mark.asyncio
async def test_memory_cache_exists_expired(memory_cache):
    await memory_cache.set("key", "value", expire=1)
    await asyncio.sleep(1.1)
    assert await memory_cache.exists("key") is False


@pytest.mark.asyncio
async def test_memory_cache_exists_sync(memory_cache):
    memory_cache.set_sync("key", "value")
    assert memory_cache.exists_sync("key") is True
    assert memory_cache.exists_sync("missing") is False


@pytest.mark.asyncio
async def test_memory_cache_exists_expired_sync(memory_cache):
    memory_cache.set_sync("key", "value", expire=1)
    time.sleep(1.1)
    assert memory_cache.exists_sync("key") is False


@pytest.mark.asyncio
async def test_memory_cache_update_expire(memory_cache):
    await memory_cache.set("key", "value", expire=1)
    assert await memory_cache.expire("key", 5) is True
    await asyncio.sleep(1.1)
    assert await memory_cache.get("key") == "value"
    assert await memory_cache.expire("missing", 5) is False


@pytest.mark.asyncio
async def test_memory_cache_update_expire_sync(memory_cache):
    memory_cache.set_sync("key", "value", expire=1)
    assert memory_cache.expire_sync("key", 5) is True
    time.sleep(1.1)
    assert memory_cache.get_sync("key") == "value"
    assert memory_cache.expire_sync("missing", 5) is False


@pytest.mark.asyncio
async def test_memory_cache_ttl(memory_cache):
    await memory_cache.set("key", "value", expire=10)
    ttl = await memory_cache.ttl("key")
    assert 0 < ttl <= 10

    await memory_cache.set("persistent", "value")
    assert await memory_cache.ttl("persistent") == -1

    assert await memory_cache.ttl("missing") == -2


@pytest.mark.asyncio
async def test_memory_cache_ttl_expired(memory_cache):
    await memory_cache.set("key", "value", expire=1)
    await asyncio.sleep(1.1)
    assert await memory_cache.ttl("key") == -2


@pytest.mark.asyncio
async def test_memory_cache_ttl_sync(memory_cache):
    memory_cache.set_sync("key", "value", expire=10)
    ttl = memory_cache.ttl_sync("key")
    assert 0 < ttl <= 10

    memory_cache.set_sync("persistent", "value")
    assert memory_cache.ttl_sync("persistent") == -1

    assert memory_cache.ttl_sync("missing") == -2


@pytest.mark.asyncio
async def test_memory_cache_ttl_expired_sync(memory_cache):
    memory_cache.set_sync("key", "value", expire=1)
    time.sleep(1.1)
    assert memory_cache.ttl_sync("key") == -2


@pytest.mark.asyncio
async def test_memory_cache_keys(memory_cache):
    await memory_cache.set("key1", "value")
    await memory_cache.set("key2", "value")
    await memory_cache.set("other", "value")

    keys = await memory_cache.keys("key*")
    assert len(keys) == 2
    assert "key1" in keys
    assert "key2" in keys

    all_keys = await memory_cache.keys()
    assert len(all_keys) == 3


@pytest.mark.asyncio
async def test_memory_cache_keys_expired(memory_cache):
    await memory_cache.set("key1", "value", expire=1)
    await memory_cache.set("key2", "value")
    await asyncio.sleep(1.1)

    keys = await memory_cache.keys()
    assert len(keys) == 1
    assert keys[0] == "key2"


@pytest.mark.asyncio
async def test_memory_cache_keys_sync(memory_cache):
    memory_cache.set_sync("key1", "value")
    memory_cache.set_sync("key2", "value")
    memory_cache.set_sync("other", "value")

    keys = memory_cache.keys_sync("key*")
    assert len(keys) == 2
    assert "key1" in keys
    assert "key2" in keys

    all_keys = memory_cache.keys_sync()
    assert len(all_keys) == 3


@pytest.mark.asyncio
async def test_memory_cache_keys_expired_sync(memory_cache):
    memory_cache.set_sync("key1", "value", expire=1)
    memory_cache.set_sync("key2", "value")
    time.sleep(1.1)

    keys = memory_cache.keys_sync()
    assert len(keys) == 1
    assert keys[0] == "key2"


@pytest.mark.asyncio
async def test_memory_cache_info(memory_cache):
    await memory_cache.set("key", "value")
    info = await memory_cache.info()
    assert info["memory_cache"] is True
    assert info["total_keys"] == 1


@pytest.mark.asyncio
async def test_memory_cache_info_sync(memory_cache):
    memory_cache.set_sync("key", "value")
    info = memory_cache.info_sync()
    assert info["memory_cache"] is True
    assert info["total_keys"] == 1


@pytest.mark.asyncio
async def test_memory_cache_clear(memory_cache):
    await memory_cache.set("key1", "value")
    await memory_cache.set("key2", "value")
    count = await memory_cache.clear()
    assert count == 2
    assert await memory_cache.keys() == []


@pytest.mark.asyncio
async def test_memory_cache_clear_sync(memory_cache):
    memory_cache.set_sync("key1", "value")
    memory_cache.set_sync("key2", "value")
    count = memory_cache.clear_sync()
    assert count == 2
    assert memory_cache.keys_sync() == []


@pytest.mark.asyncio
async def test_memory_cache_ping(memory_cache):
    assert await memory_cache.ping() is True
    assert memory_cache.ping_sync() is True
