import asyncio
import functools


def asinglton(coro):
    sentinel = instance = object()
    lock = asyncio.Lock()

    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        nonlocal instance
        if instance is sentinel:
            async with lock:
                if instance is sentinel:
                    instance = await coro(*args, **kwargs)
        return instance

    return wrapper
