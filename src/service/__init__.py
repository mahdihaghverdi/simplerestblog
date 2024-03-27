from typing import TypeVar, Generic

from src.core.redis_db import RedisClient

R = TypeVar("R")


class Service(Generic[R]):
    def __init__(self, repo: R | None, redis_client: RedisClient | None = None):
        self.repo: R = repo
        self.redis_client = redis_client
