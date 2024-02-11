from src.core.config import settings
from src.core.enums import UserRolesEnum
from src.core.schemas import TokenData
from src.core.security import create_access_token


class TestGetByUsername:
    def test_user_not_found(self, client, create_admin, admin_access_token):
        response = client.get(
            f"{settings.PREFIX}/users/mahdi",
            headers={"Authorization": f"Bearer {admin_access_token}"},
        )
        assert response.status_code == 400, response.text

    def test_admin_request_itself(self, client, create_admin, admin_access_token):
        response = client.get(
            f"{settings.PREFIX}/users/admin",
            headers={"Authorization": f"Bearer {admin_access_token}"},
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "admin"

    def test_admin_request_another(self, client, create_admin, admin_access_token):
        client.post(
            f"{settings.PREFIX}/users/signup",
            json={"username": "mahdi", "password": "12345678"},
        )
        response = client.get(
            f"{settings.PREFIX}/users/mahdi",
            headers={"Authorization": f"Bearer {admin_access_token}"},
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "mahdi"

    def test_user_requests_another(self, client, create_admin):
        client.post(
            f"{settings.PREFIX}/users/signup",
            json={"username": "mahdi", "password": "12345678"},
        )
        access_token = create_access_token(
            TokenData(username="mahdi", role=UserRolesEnum.USER),
        )

        response = client.get(
            f"{settings.PREFIX}/users/admin",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401, response.text

    def test_user_requests_itself(self, client, create_admin):
        client.post(
            f"{settings.PREFIX}/users/signup",
            json={"username": "mahdi", "password": "12345678"},
        )
        access_token = create_access_token(
            TokenData(username="mahdi", role=UserRolesEnum.USER),
        )

        response = client.get(
            f"{settings.PREFIX}/users/mahdi",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "mahdi"
