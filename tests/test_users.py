from src.core.config import settings
from src.core.enums import UserRolesEnum, APIPrefixesEnum
from src.core.schemas import UserOutSchema, AccessTokenData
from src.core.security import encode_access_token

basic_url = f"{settings.PREFIX}/{APIPrefixesEnum.USERS.value}"


def test_signup(client):
    response = client.post(
        f"{basic_url}/signup",
        json={"username": "Mahdi", "password": "12345678"},
    )
    assert response.status_code == 201, response.text

    data = UserOutSchema(**response.json())
    assert data.username == "mahdi"
    for k, v in data.model_dump().items():
        if k in ["username", "qr_img"]:
            continue
        assert v is None


def test_signup_with_data(client):
    data = {
        "username": "Mahdi",
        "password": "12345678",
        "name": "Mahdi Haghverdi",
        "bio": "Hi I am a writer",
        "email": "mahdi@mahdi.com",
        "telegram": "@pyeafp",
        "instagram": "mah.dihaghverdi",
        "twitter": "@mliewpl",
    }

    response = client.post(f"{basic_url}/signup", json=data)
    assert response.status_code == 201, response.text

    got = UserOutSchema(**response.json())
    assert got.username == data["username"].lower()
    assert got.name == data["name"]
    assert got.bio == data["bio"]
    assert got.email == data["email"]
    assert got.telegram == f'https://t.me/{data["telegram"][1:]}'
    assert got.instagram == f'https://instagram.com/{data["instagram"]}'
    assert got.twitter == f'https://x.com/@{data["twitter"][1:]}'


def test_signup_duplicate(client):
    client.post(
        f"{basic_url}/signup",
        json={"username": "Mahdi", "password": "12345678"},
    )
    response = client.post(
        f"{basic_url}/signup",
        json={"username": "Mahdi", "password": "12345678"},
    )
    assert response.status_code == 400, response.text
    assert "mahdi" in response.json()["detail"]


class TestAuth:
    username = "mahdi"
    password = "12345678"

    @property
    def data(self):
        return {"username": TestAuth.username, "password": TestAuth.password}

    @property
    def access_token_data(self):
        d = self.data
        d["grant_type"] = "password"
        return d

    def test_access_token(self, client, create_mahdi):
        response = client.post(
            f"{settings.PREFIX}/auth/access-token",
            data=self.access_token_data,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        access_token, token_type = data["access_token"], data["token_type"]
        assert access_token
        assert token_type.lower() == "bearer"

    def test_access_token_wrong_credentials(self, client, create_mahdi):
        response = client.post(
            f"{settings.PREFIX}/auth/access-token",
            data={
                "username": "mahdi",
                "grant_type": "password",
                "password": "12345677",
            },
        )
        assert response.status_code == 401, response.text

    def test_not_authorized(self, client):
        response = client.get(f"{basic_url}/me")
        assert response.status_code == 401, response.text

    def test_bad_token_username_none(self, client):
        client.post(f"{basic_url}/signup", json=self.data)
        access_token = encode_access_token(AccessTokenData(username=None))
        response = client.get(
            f"{basic_url}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401, response.text

    def test_bad_token_role_none(self, client):
        client.post(f"{basic_url}/signup", json=self.data)
        access_token = encode_access_token(AccessTokenData(username="mahdi", role=None))
        response = client.get(
            f"{basic_url}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401, response.text

    def test_bad_token_another_encoding(self, client):
        client.post(f"{basic_url}/signup", json=self.data)

        settings.ALGORITHM = "HS512"
        response = client.post(
            f"{settings.PREFIX}/auth/access-token",
            data=self.access_token_data,
        )
        access_token = response.json()["access_token"]

        settings.ALGORITHM = "HS256"
        response = client.get(
            f"{basic_url}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401, response.text


def test_users_me(client, admin_access_token):
    response = client.get(
        f"{basic_url}/me",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["username"] == "admin"
    for k, v in data.items():
        if k == "username":
            continue
        assert v is None


def test_users_me_with_data(client):
    data = {
        "username": "Mahdi",
        "password": "12345678",
        "name": "Mahdi Haghverdi",
        "bio": "Hi I am a writer",
        "email": "mahdi@mahdi.com",
        "telegram": "@pyeafp",
        "instagram": "mah.dihaghverdi",
        "twitter": "@mliewpl",
    }

    client.post(f"{basic_url}/signup", json=data)
    access_token = encode_access_token(
        AccessTokenData(username="mahdi", role=UserRolesEnum.USER),
    )

    response = client.get(
        f"{basic_url}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, response.text

    got = UserOutSchema(**response.json())
    assert got.username == data["username"].lower()
    assert got.name == data["name"]
    assert got.bio == data["bio"]
    assert got.email == data["email"]
    assert got.telegram == f'https://t.me/{data["telegram"][1:]}'
    assert got.instagram == f'https://instagram.com/{data["instagram"]}'
    assert got.twitter == f'https://x.com/@{data["twitter"][1:]}'
