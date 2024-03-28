import asyncio

import pytest
from sqlalchemy import insert
from starlette.testclient import TestClient

from src.app import app
from src.core.config import settings
from src.core.database import get_db_session
from src.core.enums import APIPrefixesEnum
from src.core.redis_db import get_redis_client
from src.core.security import hash_password
from src.repository.models import UserModel, Base
from tests.database import get_db_mock, ASessionMock, AEngineMock
from tests.redis_db import get_redis_client_mock, clear_database

app.dependency_overrides[get_db_session] = get_db_mock
app.dependency_overrides[get_redis_client] = get_redis_client_mock

base_url = f"{settings.PREFIX}/"


async def create_all():
    async with AEngineMock.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with AEngineMock.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client():
    asyncio.run(create_all())
    clear_database()
    yield TestClient(app=app)
    clear_database()
    asyncio.run(drop_all())


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
    # return encode_access_token(
    #     AccessTokenData(username="admin", role=UserRolesEnum.ADMIN),
    # )
    pass


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
    # return encode_access_token(
    #     AccessTokenData(username="mahdi", role=UserRolesEnum.USER),
    # )
    pass


@pytest.fixture
def mahdi_auth_headers(mahdi_access_token):
    return {"Authorization": f"Bearer {mahdi_access_token}"}


@pytest.fixture
def post_id_fixture(client, mahdi_auth_headers):
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


@pytest.fixture
def comment_id_fixture(client, mahdi_auth_headers, post_id_fixture):
    comment_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id_fixture}",
        json={"comment": "comment"},
        headers=mahdi_auth_headers,
    ).json()["id"]
    return comment_id
