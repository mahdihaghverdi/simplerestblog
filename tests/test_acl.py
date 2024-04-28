from abc import ABC, abstractmethod

from src.core.config import settings
from src.core.enums import APIPrefixesEnum
from tests import BaseTest
from tests import base_url

draft_data = {"title": "title", "body": "body"}

users_basic_url = base_url + f"{APIPrefixesEnum.USERS.value}"
drafts_basic_url = base_url + f"{APIPrefixesEnum.DRAFTS.value}"
posts_basic_url = base_url + f"{APIPrefixesEnum.POSTS.value}"
comments_basic_url = base_url + f"{APIPrefixesEnum.COMMENTS.value}"


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


class TestGetByUsername(PermissionABC, BaseTest):
    def test_not_found(self, client, refreshed_admin):
        response = client.get(
            f"{users_basic_url}/mahdi", **self.headers_cookies(refreshed_admin)
        )
        assert response.status_code == 404, response.text

    def test_admin_request_itself(self, client, refreshed_admin):
        response = client.get(
            f"{users_basic_url}/admin", **self.headers_cookies(refreshed_admin)
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "admin"

    def test_admin_request_another(self, client, refreshed_admin, signup_mahdi):
        response = client.get(
            f"{users_basic_url}/mahdi", **self.headers_cookies(refreshed_admin)
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "mahdi"

    def test_user_requests_itself(self, client, refreshed_mahdi):
        response = client.get(
            f"{users_basic_url}/mahdi", **self.headers_cookies(refreshed_mahdi)
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == "mahdi"

    def test_user_requests_another(self, client, signup_admin, refreshed_mahdi):
        response = client.get(
            f"{users_basic_url}/admin", **self.headers_cookies(refreshed_mahdi)
        )
        assert response.status_code == 401, response.text


def create_draft(client, headers, cookies):
    draft_id = client.post(
        f"{drafts_basic_url}/", headers=headers, cookies=cookies, json=draft_data
    ).json()["id"]
    return draft_id


class TestGetOneDraft(PermissionABC, BaseTest):
    username_path: str = f"{drafts_basic_url}/" + "{username}/{draft_id}"

    def test_not_found(self, client, refreshed_admin):
        response = client.get(
            f"{drafts_basic_url}/1", **self.headers_cookies(refreshed_admin)
        )
        assert response.status_code == 404, response.text

    def test_admin_request_itself(self, client, refreshed_admin):
        headers, cookies = self.headers_cookies_tuple(refreshed_admin)
        draft_id = create_draft(client, headers=headers, cookies=cookies)
        url = self.username_path.format(draft_id=draft_id, username="admin")

        response = client.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["title"] == draft_data["title"]
        assert data["body"] == draft_data["body"]
        assert data["username"] == "admin"

    def test_admin_request_another(self, client, refreshed_admin, refreshed_mahdi):
        admin_headers, admin_cookies = self.headers_cookies_tuple(refreshed_admin)
        mahdi_headers, mahdi_cookies = self.headers_cookies_tuple(refreshed_mahdi)
        draft_id = create_draft(client, headers=mahdi_headers, cookies=mahdi_cookies)
        url = self.username_path.format(draft_id=draft_id, username="mahdi")

        response = client.get(url, headers=admin_headers, cookies=admin_cookies)
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["title"] == draft_data["title"]
        assert data["body"] == draft_data["body"]
        assert data["username"] == "mahdi"

    def test_user_requests_itself(self, client, refreshed_mahdi):
        headers, cookies = self.headers_cookies_tuple(refreshed_mahdi)
        draft_id = create_draft(client, headers=headers, cookies=cookies)
        url = self.username_path.format(draft_id=draft_id, username="mahdi")

        response = client.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["title"] == draft_data["title"]
        assert data["body"] == draft_data["body"]
        assert data["username"] == "mahdi"

    def test_user_requests_another(self, client, signup_admin, refreshed_mahdi):
        headers, cookies = self.headers_cookies_tuple(refreshed_mahdi)
        url = self.username_path.format(draft_id=1, username="admin")

        response = client.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 401, response.text


class TestGetAllDrafts(PermissionABC, BaseTest):
    username_path = f"{drafts_basic_url}/" + "all/{username}"

    def test_admin_request_itself(self, client, refreshed_admin):
        headers, cookies = self.headers_cookies_tuple(refreshed_admin)
        create_draft(client, headers, cookies)
        create_draft(client, headers, cookies)

        url = self.username_path.format(username="admin")

        response = client.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 2
        for d in data:
            assert d["title"] == draft_data["title"]

    def test_admin_request_another(self, client, refreshed_admin, refreshed_mahdi):
        admin_headers, admin_cookies = self.headers_cookies_tuple(refreshed_admin)
        mahdi_headers, mahdi_cookies = self.headers_cookies_tuple(refreshed_mahdi)
        create_draft(client, headers=mahdi_headers, cookies=mahdi_cookies)
        url = self.username_path.format(username="mahdi")

        response = client.get(url, headers=admin_headers, cookies=admin_cookies)
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 1
        for d in data:
            assert d["title"] == draft_data["title"]

    def test_user_requests_itself(self, client, refreshed_mahdi):
        headers, cookies = self.headers_cookies_tuple(refreshed_mahdi)
        create_draft(client, headers=headers, cookies=cookies)
        create_draft(client, headers=headers, cookies=cookies)
        url = self.username_path.format(username="mahdi")

        response = client.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 2
        for d in data:
            assert d["title"] == draft_data["title"]

    def test_user_requests_another(self, client, signup_admin, refreshed_mahdi):
        headers, cookies = self.headers_cookies_tuple(refreshed_mahdi)
        url = self.username_path.format(username="admin")

        response = client.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 401, response.text


def create_post(client, headers, cookies, draft_id):
    post_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/publish/{draft_id}",
        json={"tags": ["tag1", "tag2"], "slug": "slug"},
        headers=headers,
        cookies=cookies,
    ).json()["id"]
    return post_id


def create_comment(client, headers, cookies, post_id):
    comment_id = client.post(
        f"{settings.PREFIX}/{APIPrefixesEnum.COMMENTS.value}/{post_id}",
        json={"comment": "comment"},
        headers=headers,
        cookies=cookies,
    ).json()["id"]
    return comment_id


class TestDeleteComment(PermissionABC, BaseTest):
    def test_admin_request_itself(self, client, refreshed_admin):
        headers, cookies = self.headers_cookies_tuple(refreshed_admin)

        draft_id = create_draft(client, headers, cookies)
        post_id = create_post(client, headers, cookies, draft_id)
        comment_id = create_comment(client, headers, cookies, post_id)

        response = client.delete(
            f"{comments_basic_url}/{post_id}/{comment_id}",
            headers=headers,
            cookies=cookies,
        )
        assert response.status_code == 204, response.text

        comments = client.get(f"{comments_basic_url}/{post_id}").json()
        assert len(comments) == 0

    def test_admin_request_another(self, client, refreshed_admin, refreshed_mahdi):
        headers, cookies = self.headers_cookies_tuple(refreshed_admin)

        draft_id = create_draft(client, headers, cookies)
        post_id = create_post(client, headers, cookies, draft_id)
        comment_id = create_comment(client, headers, cookies, post_id)

        response = client.delete(
            f"{comments_basic_url}/{post_id}/{comment_id}",
            headers=headers,
            cookies=cookies,
        )
        assert response.status_code == 204, response.text

        comments = client.get(f"{comments_basic_url}/{post_id}").json()
        assert len(comments) == 0

    def test_user_requests_itself(self, client, refreshed_mahdi):
        headers, cookies = self.headers_cookies_tuple(refreshed_mahdi)

        draft_id = create_draft(client, headers, cookies)
        post_id = create_post(client, headers, cookies, draft_id)
        comment_id = create_comment(client, headers, cookies, post_id)

        response = client.delete(
            f"{comments_basic_url}/{post_id}/{comment_id}",
            headers=headers,
            cookies=cookies,
        )
        assert response.status_code == 204, response.text

        comments = client.get(f"{comments_basic_url}/{post_id}").json()
        assert len(comments) == 0

    def test_user_requests_another(self, client, refreshed_admin, refreshed_mahdi):
        headers, cookies = self.headers_cookies_tuple(refreshed_admin)
        mheaders, mcookies = self.headers_cookies_tuple(refreshed_mahdi)

        draft_id = create_draft(client, headers, cookies)
        post_id = create_post(client, headers, cookies, draft_id)
        comment_id = create_comment(client, headers, cookies, post_id)

        response = client.delete(
            f"{comments_basic_url}/{post_id}/{comment_id}",
            headers=mheaders,
            cookies=mcookies,
        )
        assert response.status_code == 401, response.text
