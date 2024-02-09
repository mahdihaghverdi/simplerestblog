import os
import subprocess

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.testclient import TestClient

from src.core.config import settings
from src.core.database import get_db
from src.web.app import app

AEngineMock = create_async_engine(str(settings.TEST_DATABASE_URL), poolclass=NullPool)
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


@pytest.fixture(scope="function")
def client():
    os.environ["DATABASE_URL"] = f"{settings.TEST_DATABASE_URL}"
    subprocess.call(["alembic", "upgrade", "head"])
    try:
        yield TestClient(app=app)
    finally:
        os.environ["DATABASE_URL"] = f"{settings.TEST_DATABASE_URL}"
        subprocess.call(["alembic", "downgrade", "base"])
