import asyncio

import pytest
from starlette.testclient import TestClient

from src.app import app
from src.core.config import settings
from src.core.database import get_db_sessionmaker
from src.core.enums import APIPrefixesEnum
from src.core.redis_db import get_redis_client
from src.repository.models import Base
from tests.auth.conftest import (  # noqa
    signup_mahdi,
    signup_admin,
    login_mahdi,
    login_admin,
    verified_mahdi,
    verified_admin,
    refreshed_mahdi,
    refreshed_admin,
    get_mahdi_totp_hash,
    get_admin_totp_hash,
)
from tests.shared.database import get_session_maker_mock, AEngineMock
from tests.shared.redis_db import get_redis_client_mock, clear_database

app.dependency_overrides[get_db_sessionmaker] = get_session_maker_mock
app.dependency_overrides[get_redis_client] = get_redis_client_mock


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
