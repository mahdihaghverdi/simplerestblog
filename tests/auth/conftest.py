import asyncio
from collections import namedtuple

import pytest
from sqlalchemy import select

from src.core.enums import APIPrefixesEnum
from src.repository.models import UserModel
from tests.conftest import base_url
from tests.database import ASessionMock

base_url = base_url + f"{APIPrefixesEnum.AUTH.value}"

data = {"username": "mahdi", "password": "12345678"}


@pytest.fixture
def signup_mahdi(client):
    client.post(base_url + "/signup", json=data)
    yield


LoginData = namedtuple("LoginData", "refresh_token, csrf_token")


@pytest.fixture
def login_mahdi(client, signup_mahdi):
    response = client.post(base_url + "/login", json=data)
    yield LoginData(
        response.cookies.get("Refresh-Token"), response.headers.get("x-csrf-token")
    )


@pytest.fixture
def get_mahdi_totp_hash():
    async def setup():
        async with ASessionMock() as session:
            async with session.begin():
                stmt = select(UserModel.totp_hash).where(
                    UserModel.username == data["username"]
                )
                return (await session.execute(stmt)).scalar_one()

    return asyncio.run(setup())
