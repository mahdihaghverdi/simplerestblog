import asyncio

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.testclient import TestClient

from src.core.config import settings
from src.core.database import get_db
from src.repository.models import Base
from src.web.app import app

AEngineMock = create_async_engine(str(settings.DATABASE_URL), poolclass=NullPool)
ASessionMock = async_sessionmaker(
    bind=AEngineMock,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_mock():
    db = ASessionMock()
    try:
        yield db
    finally:
        await db.close()


app.dependency_overrides[get_db] = get_db_mock


async def create():
    async with AEngineMock.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop():
    async with AEngineMock.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client() -> TestClient:
    asyncio.run(create())
    try:
        return TestClient(app)
    finally:
        asyncio.run(drop())
