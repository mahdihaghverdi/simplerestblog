from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings
from src.core.utils import asingleton

AEngine = create_async_engine(settings.DATABASE_URL)

ASession = async_sessionmaker(bind=AEngine, expire_on_commit=False)


@asingleton
async def get_db_session() -> AsyncSession:
    return ASession()
