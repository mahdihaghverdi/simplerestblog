from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings
from src.core.utils import asingleton

AEngineMock = create_async_engine(str(settings.TEST_DATABASE_URL), poolclass=NullPool)
ASessionMock = async_sessionmaker(
    bind=AEngineMock,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asingleton
async def get_db_mock():
    return ASessionMock()
