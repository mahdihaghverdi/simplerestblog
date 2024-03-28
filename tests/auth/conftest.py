import pytest

from src.core.enums import APIPrefixesEnum
from tests.conftest import base_url

base_url = base_url + f"{APIPrefixesEnum.AUTH.value}"


@pytest.fixture
def signup_mahdi(client):
    client.post(base_url + "/signup", json={"username": "mahdi", "password": "12345678"})
    yield
