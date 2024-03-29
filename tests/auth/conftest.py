import asyncio
from collections import namedtuple

import pytest
from pyotp import totp
from sqlalchemy import select

from src.core.enums import APIPrefixesEnum
from src.repository.models import UserModel
from tests.conftest import base_url
from tests.database import ASessionMock

base_url = base_url + f"{APIPrefixesEnum.AUTH.value}"

username = "mahdi"
password = "12345678"
simple_signup_data = {"username": username, "password": password}
signup_data = {
    "username": "Mahdi",
    "password": "12345678",
    "name": "Mahdi Haghverdi",
    "bio": "Hi I am a writer",
    "email": "mahdi@mahdi.com",
    "telegram": "@pyeafp",
    "instagram": "mah.dihaghverdi",
    "twitter": "@mliewpl",
}
login_data = {"username": username, "password": password}
data = {"username": "mahdi", "password": "12345678"}

LoginData = namedtuple("LoginData", "refresh_token, csrf_token")

RefreshedData = namedtuple("RefreshedData", "refresh_token, access_token, csrf_token")


@pytest.fixture
def signup_mahdi(client):
    client.post(base_url + "/signup", json=data)
    yield


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


@pytest.fixture
def verified_mahdi(client, login_mahdi, get_mahdi_totp_hash):
    totp_hash = get_mahdi_totp_hash
    uri = totp.TOTP(totp_hash)
    current = uri.now()

    client.post(
        base_url + "/verify",
        params={"code": str(current)},
        headers={"Authorization": f"Bearer {login_mahdi.csrf_token}"},
        cookies={"Refresh-Token": login_mahdi.refresh_token},
    )
    yield login_mahdi


@pytest.fixture
def refreshed_mahdi(client, verified_mahdi):
    response = client.post(
        base_url + "/refresh",
        headers={"Authorization": f"Bearer {verified_mahdi.csrf_token}"},
        cookies={"Refresh-Token": verified_mahdi.refresh_token},
    )
    refresh_token = response.cookies.get("Refresh-Token")
    access_token = response.cookies.get("Access-Token")
    x_csrf_token = response.headers.get("x-csrf-token")

    return RefreshedData(refresh_token, access_token, x_csrf_token)
