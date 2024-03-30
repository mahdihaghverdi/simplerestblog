from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings

AEngine = create_async_engine(settings.DATABASE_URL)

ASession = async_sessionmaker(bind=AEngine, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    return ASession()
