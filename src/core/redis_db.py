import pickle

import redis
from redis.asyncio.client import Redis

from src.core.config import settings
from src.core.exceptions import DatabaseConnectionError
from src.core.utils import asingleton


class _RedisSerializer:
    def __init__(self, protocol=None):
        self.protocol = pickle.HIGHEST_PROTOCOL if protocol is None else protocol

    def dumps(self, obj):
        if type(obj) is int:  # noqa E721
            return obj
        return pickle.dumps(obj, self.protocol)

    def loads(self, data):
        try:
            return int(data)
        except ValueError:
            return pickle.loads(data)


class RedisClient:
    def __init__(self):
        self.redis = Redis.from_url(settings.SRB_REDIS_CACHE_URL, max_connections=100)
        self._serializer = _RedisSerializer()

    async def ping(self):
        return await self.redis.ping()

    async def get(self, name: str, default=None):
        got = await self.redis.get(name)
        return default if got is None else self._serializer.loads(got)

    async def set(self, name, value, timeout):
        value = self._serializer.dumps(value)
        if timeout == 0:
            await self.redis.delete(name)
        else:
            await self.redis.set(name, value, ex=timeout)

    async def delete(self, *names):
        return bool(await self.redis.delete(*names))

    async def ttl(self, name) -> int:
        return await self.redis.ttl(name)

    async def close(self):
        await self.redis.aclose()


@asingleton
async def get_redis_client() -> RedisClient:
    rd = RedisClient()
    try:
        await rd.ping()
    except (redis.exceptions.ConnectionError, ConnectionRefusedError):
        raise DatabaseConnectionError("Redis connection is not initialized")
    else:
        return rd
