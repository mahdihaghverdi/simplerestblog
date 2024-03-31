from src.core.utils import asingleton

database = {}


class RedisClientMock:
    async def get(self, name: str, default=None):
        return database.get(name, default)

    async def set(self, name, value, timeout):
        database[name] = value
        return True

    async def delete(self, *names):
        for name in names:
            database.pop(name)

    async def ttl(self, name) -> int:
        return 100


def clear_database():
    database.clear()


@asingleton
async def get_redis_client_mock():
    return RedisClientMock()
