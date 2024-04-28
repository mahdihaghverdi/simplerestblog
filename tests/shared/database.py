from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings

AEngineMock = create_async_engine(str(settings.SRB_TEST_DATABASE_URL), poolclass=NullPool)
ASessionMock = async_sessionmaker(
    bind=AEngineMock,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session_maker_mock():
    return ASessionMock
