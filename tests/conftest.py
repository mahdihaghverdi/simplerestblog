import asyncio

import pytest
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.testclient import TestClient

from src.app import app
from src.core.config import settings
from src.core.database import get_db
from src.core.enums import UserRolesEnum, APIPrefixesEnum
from src.core.schemas import TokenData
from src.core.security import hash_password, create_access_token
from src.repository.models import UserModel, Base

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


@pytest.fixture
def create_admin():
    async def setup():
        async with ASessionMock() as session:
            async with session.begin():
                stmt = insert(UserModel).values(
                    username="admin",
                    password=hash_password("1"),
                    role="ADMIN",
                )
                await session.execute(stmt)

    asyncio.run(setup())


@pytest.fixture
def admin_access_token(create_admin):
    return create_access_token(
        TokenData(username="admin", role=UserRolesEnum.ADMIN),
    )


@pytest.fixture
def admin_auth_headers(admin_access_token):
    return {"Authorization": f"Bearer {admin_access_token}"}


@pytest.fixture
def create_mahdi():
    async def setup():
        async with ASessionMock() as session:
            async with session.begin():
                stmt = insert(UserModel).values(
                    username="mahdi",
                    password=hash_password("12345678"),
                    role="USER",
                )
                await session.execute(stmt)

    asyncio.run(setup())


@pytest.fixture
def mahdi_access_token(create_mahdi):
    return create_access_token(
        TokenData(username="mahdi", role=UserRolesEnum.USER),
    )


@pytest.fixture
def mahdi_auth_headers(mahdi_access_token):
    return {"Authorization": f"Bearer {mahdi_access_token}"}


@pytest.fixture
def post_id(client, mahdi_auth_headers):
    draft_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}",
        json={"title": "title", "body": "body"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    post_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "slug"},
        headers=mahdi_auth_headers,
    ).json()["id"]

    return post_id


async def create_all():
    async with AEngineMock.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with AEngineMock.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client():
    asyncio.run(create_all())
    yield TestClient(app=app)
    asyncio.run(drop_all())
