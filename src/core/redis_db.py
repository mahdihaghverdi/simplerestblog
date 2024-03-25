import pickle

from redis.asyncio.client import Redis

from src.core.config import settings


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
        self.redis = Redis.from_url(settings.REDIS_CACHE_URL, max_connections=100)
        self._serializer = _RedisSerializer()

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


def get_redis_db():
    return RedisClient()
