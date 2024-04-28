from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings

AEngine = create_async_engine(settings.SRB_PG_URL, pool_size=30, max_overflow=60)

ASession = async_sessionmaker(bind=AEngine, expire_on_commit=False)


async def get_db_sessionmaker() -> async_sessionmaker:
    return ASession
