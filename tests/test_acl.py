from abc import ABC, abstractmethod

from src.core.config import settings
from src.core.enums import UserRolesEnum
from src.core.schemas import TokenData
from src.core.security import create_access_token

draft_data = {"title": "title", "body": "body"}


class PermissionABC(ABC):
    @abstractmethod
    def test_not_found(self, *args):
        pass

    @abstractmethod
    def test_admin_request_itself(self, *args):
        pass

    @abstractmethod
    def test_admin_request_another(self, *args):
        pass

    @abstractmethod
    def test_user_requests_itself(self, *args):
        pass

    @abstractmethod
    def test_user_requests_another(self, *args):
        pass


# TODO: speedup the tests using the fixtures
class TestGetByUsername(PermissionABC):
    def test_not_found(self, client, create_admin, admin_auth_headers):
        response = client.get(
            f"{settings.PREFIX}/users/mahdi",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_admin_request_itself(self, client, create_admin, admin_auth_headers):
        response = client.get(
            f"{settings.PREFIX}/users/admin",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "admin"

    def test_admin_request_another(self, client, create_admin, admin_auth_headers):
        client.post(
            f"{settings.PREFIX}/users/signup",
            json={"username": "mahdi", "password": "12345678"},
        )
        response = client.get(
            f"{settings.PREFIX}/users/mahdi",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "mahdi"

    def test_user_requests_itself(self, client):
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

    def test_user_requests_another(self, client):
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


def create_draft(client, headers):
    draft_id = client.post(
        f"{settings.PREFIX}/drafts",
        json=draft_data,
        headers=headers,
    ).json()["id"]
    return draft_id


class TestGetOneDraft(PermissionABC):
    basic_path: str = f"{settings.PREFIX}/drafts/" + "{draft_id}"
    username_path: str = f"{settings.PREFIX}/drafts/" + "{username}/{draft_id}"

    def test_not_found(self, client, create_admin, admin_auth_headers):
        response = client.get(
            f"{settings.PREFIX}/drafts/1",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_admin_request_itself(self, client, create_admin, admin_auth_headers):
        draft_id = create_draft(client, admin_auth_headers)

        response = client.get(
            self.basic_path.format(draft_id=draft_id),
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["title"] == draft_data["title"]
        assert data["body"] == draft_data["body"]
        assert data["username"] == "admin"

    def test_admin_request_another(
        self,
        client,
        create_admin,
        admin_auth_headers,
        create_mahdi,
        mahdi_auth_headers,
    ):
        draft_id = create_draft(client, mahdi_auth_headers)
        response = client.get(
            self.username_path.format(draft_id=draft_id, username="mahdi"),
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["title"] == draft_data["title"]
        assert data["body"] == draft_data["body"]
        assert data["username"] == "mahdi"

    def test_user_requests_itself(self, client, create_mahdi, mahdi_auth_headers):
        draft_id = create_draft(client, mahdi_auth_headers)
        response = client.get(
            self.basic_path.format(draft_id=draft_id),
            headers=mahdi_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["title"] == draft_data["title"]
        assert data["body"] == draft_data["body"]
        assert data["username"] == "mahdi"

    def test_user_requests_another(
        self,
        client,
        create_admin,
        admin_auth_headers,
        create_mahdi,
        mahdi_auth_headers,
    ):
        draft_id = create_draft(client, admin_auth_headers)
        response = client.get(
            self.username_path.format(username="admin", draft_id=draft_id),
            headers=mahdi_auth_headers,
        )
        assert response.status_code == 401, response.text
