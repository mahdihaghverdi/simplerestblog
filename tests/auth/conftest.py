from collections import namedtuple

import pytest

from src.core.enums import APIPrefixesEnum
from tests.conftest import base_url

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
