from src.core.config import settings
from src.core.schemas import UserOutSchema


def test_signup(client):
    response = client.post(
        f"{settings.PREFIX}/users/signup",
        json={"username": "Mahdi", "password": "12345678"},
    )
    assert response.status_code == 201, response.text

    data = UserOutSchema(**response.json())
    assert data.username == "mahdi"
    for k, v in data.model_dump().items():
        if k == "username":
            continue
        assert v is None


def test_signup_with_data(client):
    data = {
        "username": "Mahdi",
        "password": "12345678",
        "name": "Mahdi Haghverdi",
        "bio": "Hi I am a writer",
        "email": "mahdi@mahdi.com",
        "telegram": "pyeafp",
        "instagram": "mah.dihaghverdi",
        "twitter": "mliewpl",
    }

    response = client.post(f"{settings.PREFIX}/users/signup", json=data)
    assert response.status_code == 201, response.text

    got = UserOutSchema(**response.json())
    assert got.username == data["username"].lower()
    assert got.name == data["name"]
    assert got.bio == data["bio"]
    assert got.email == data["email"]
    assert got.telegram == f'https://t.me/{data["telegram"]}'
    assert got.instagram == f'https://instagram.com/{data["instagram"]}'
    assert got.twitter == f'https://x.com/@{data["twitter"]}'


def test_signup_duplicate(client):
    client.post(
        f"{settings.PREFIX}/users/signup",
        json={"username": "Mahdi", "password": "12345678"},
    )
    response = client.post(
        f"{settings.PREFIX}/users/signup",
        json={"username": "Mahdi", "password": "12345678"},
    )
    assert response.status_code == 400, response.text
