from src.core.utils import asingleton


class RedisClientMock:
    def __init__(self):
        self.database = {}

    async def get(self, name: str, default=None):
        return self.database.get(name, default)

    async def set(self, name, value, timeout):
        self.database[name] = value
        return True

    async def delete(self, *names):
        for name in names:
            self.database.pop(name)

    async def ttl(self, name) -> int:
        return 100


@asingleton
async def get_redis_client_mock():
    return RedisClientMock()
