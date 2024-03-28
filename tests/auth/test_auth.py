from http import HTTPStatus

from src.core.schemas import UserOutSchema
from .conftest import base_url

signup_url = base_url + "/signup"
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


def test_signup_simple(client):
    response = client.post(signup_url, json=simple_signup_data)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["username"] == username
    for k, v in data.items():
        if k in ["username", "qr_img"]:
            continue
        assert v is None


def test_signup_complex(client):
    response = client.post(signup_url, json=signup_data)
    assert response.status_code == 201, response.text

    got = UserOutSchema(**response.json())
    assert got.username == signup_data["username"].lower()
    assert got.name == signup_data["name"]
    assert got.bio == signup_data["bio"]
    assert got.email == signup_data["email"]
    assert got.telegram == f'https://t.me/{signup_data["telegram"][1:]}'
    assert got.instagram == f'https://instagram.com/{signup_data["instagram"]}'
    assert got.twitter == f'https://x.com/@{signup_data["twitter"][1:]}'


def test_signup_duplicate(client):
    client.post(signup_url, json=simple_signup_data)
    response = client.post(signup_url, json=simple_signup_data)
    assert response.status_code == 400, response.text

    error_message = response.json()
    code_message, message = error_message["error"], error_message["details"]
    assert code_message == HTTPStatus.BAD_REQUEST.description
    assert message == f"username: {username!r} already exists!"
