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


base_url = f"{settings.PREFIX}/"


class BaseTest:
    url: str

    @staticmethod
    def extract_error_message(data):
        return data["error"], data.get("details")

    @staticmethod
    def make_auth_headers(csrf_token):
        return {"Authorization": f"Bearer {csrf_token}"}

    @staticmethod
    def make_auth_cookies(refresh_token, access_token=None):
        base = {"Refresh-Token": refresh_token}
        if access_token:
            base["Access-Token"] = access_token
            return base
        return base

    def headers_cookies(self, refreshed_namedtuple) -> dict[str, dict[str, str]]:
        headers = self.make_auth_headers(refreshed_namedtuple.csrf_token)
        cookies = self.make_auth_cookies(
            refreshed_namedtuple.refresh_token, refreshed_namedtuple.access_token
        )
        return {"headers": headers, "cookies": cookies}

    def headers_cookies_tuple(self, refreshed_namedtuple):
        _ = self.headers_cookies(refreshed_namedtuple)
        return _["headers"], _["cookies"]


users_basic_url = base_url + f"{APIPrefixesEnum.USERS.value}"
drafts_basic_url = base_url + f"{APIPrefixesEnum.DRAFTS.value}"
posts_basic_url = base_url + f"{APIPrefixesEnum.POSTS.value}"
comments_basic_url = base_url + f"{APIPrefixesEnum.COMMENTS.value}"

draft_data = {"title": "title", "body": "body"}


def create_draft(client, headers, cookies, title="title"):
    draft_data["title"] = title
    draft_id = client.post(
        f"{drafts_basic_url}/", headers=headers, cookies=cookies, json=draft_data
    ).json()["id"]
    return draft_id


def create_post(client, headers, cookies, draft_id):
    post_id = client.post(
        f"{drafts_basic_url}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "slug"},
        headers=headers,
        cookies=cookies,
    ).json()["id"]
    return post_id


def create_comment(client, headers, cookies, post_id, comment="comment"):
    comment_id = client.post(
        f"{comments_basic_url}/{post_id}",
        json={"comment": comment},
        headers=headers,
        cookies=cookies,
    ).json()["id"]
    return comment_id


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
