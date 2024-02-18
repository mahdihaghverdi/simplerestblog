from abc import ABC, abstractmethod

from src.core.config import settings
from src.core.enums import APIPrefixesEnum

draft_data = {"title": "title", "body": "body"}

users_basic_url = f"{settings.PREFIX}/{APIPrefixesEnum.USERS.value}"
drafts_basic_url = f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}"


class PermissionABC(ABC):
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


class TestGetByUsername(PermissionABC):
    def test_not_found(self, client, admin_auth_headers):
        response = client.get(
            f"{users_basic_url}/mahdi",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_admin_request_itself(self, client, admin_auth_headers):
        response = client.get(
            f"{users_basic_url}/admin",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "admin"

    def test_admin_request_another(
        self,
        client,
        admin_auth_headers,
        create_mahdi,
    ):
        response = client.get(
            f"{users_basic_url}/mahdi",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "mahdi"

    def test_user_requests_itself(self, client, mahdi_auth_headers):
        response = client.get(
            f"{users_basic_url}/mahdi",
            headers=mahdi_auth_headers,
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "mahdi"

    def test_user_requests_another(
        self,
        client,
        create_admin,
        create_mahdi,
        mahdi_auth_headers,
    ):
        response = client.get(
            f"{users_basic_url}/admin",
            headers=mahdi_auth_headers,
        )
        assert response.status_code == 401, response.text


def create_draft(client, headers):
    draft_id = client.post(
        f"{drafts_basic_url}/create",
        json=draft_data,
        headers=headers,
    ).json()["id"]
    return draft_id


class TestGetOneDraft(PermissionABC):
    basic_path: str = f"{drafts_basic_url}/" + "{draft_id}"
    username_path: str = f"{drafts_basic_url}/" + "{username}/{draft_id}"

    def test_not_found(self, client, admin_auth_headers):
        response = client.get(
            f"{drafts_basic_url}/1",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404, response.text

    def test_admin_request_itself(self, client, admin_auth_headers):
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
        admin_auth_headers,
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

    def test_user_requests_itself(self, client, mahdi_auth_headers):
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
        mahdi_auth_headers,
    ):
        response = client.get(
            self.username_path.format(username="admin", draft_id=1),
            headers=mahdi_auth_headers,
        )
        assert response.status_code == 401, response.text


class TestGetAllDrafts(PermissionABC):
    def test_admin_request_itself(self, client, admin_auth_headers):
        response = client.get(
            f"{drafts_basic_url}/all/admin",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text
        assert not response.json()

    def test_admin_request_another(self, client, admin_auth_headers, create_mahdi):
        response = client.get(
            f"{drafts_basic_url}/all/mahdi",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200, response.text
        assert not response.json()

    def test_user_requests_itself(self, client, mahdi_auth_headers):
        response = client.get(
            f"{drafts_basic_url}/all/mahdi",
            headers=mahdi_auth_headers,
        )
        assert response.status_code == 200, response.text
        assert not response.json()

    def test_user_requests_another(self, client, create_admin, mahdi_auth_headers):
        response = client.get(
            f"{drafts_basic_url}/all/admin",
            headers=mahdi_auth_headers,
        )
        assert response.status_code == 401, response.text
