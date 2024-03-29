import asyncio
import base64
from http import HTTPStatus

from pyotp import totp

from src.core.config import settings
from src.core.enums import UserRolesEnum, APIPrefixesEnum
from src.core.exceptions import CredentialsError
from src.core.schemas import UserOutSchema
from src.core.security import decode_refresh_token, decode_csrf_token, decode_access_token
from src.core.utils import sha256_username
from .conftest import base_url, simple_signup_data, username, signup_data, login_data
from ..redis_db import get_redis_client_mock


class BaseTest:
    url: str

    @staticmethod
    def extract_error_message(data):
        return data["error"], data.get("details")

    @staticmethod
    def make_auth_headers(csrf_token):
        return {"Authorization": f"Bearer {csrf_token}"}

    @staticmethod
    def make_auth_cookies(refresh_token, access_token=None):
        base = {"Refresh-Token": refresh_token}
        if access_token:
            base.update([("Access-Token", access_token)])
            return base
        return base


class RefreshTokenMixin:
    def test_not_pass_refresh_token(self, client, login_mahdi):
        response = client.post(
            self.url, headers=self.make_auth_headers(login_mahdi.csrf_token)
        )
        assert response.status_code == HTTPStatus.FORBIDDEN.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.FORBIDDEN.description
        assert message == "Refresh-Token is not provided"

    def test_invalid_refresh_token(self, client, login_mahdi):
        invalid_ref_token = login_mahdi.refresh_token.translate(str.maketrans({"a": "b"}))
        response = client.post(
            self.url,
            headers=self.make_auth_headers(login_mahdi.csrf_token),
            cookies={"Refresh-Token": invalid_ref_token},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.UNAUTHORIZED.description
        assert message == "Invalid Refresh-Token"


class TestSignup(BaseTest):
    url = base_url + "/signup"

    def test_signup_simple(self, client):
        response = client.post(self.url, json=simple_signup_data)
        assert response.status_code == 201, response.text

        data = response.json()
        assert data["username"] == username
        for k, v in data.items():
            if k in ["username", "qr_img"]:
                continue
            assert v is None

    def test_signup_complex(self, client):
        response = client.post(self.url, json=signup_data)
        assert response.status_code == 201, response.text

        got = UserOutSchema(**response.json())
        assert got.username == signup_data["username"].lower()
        assert got.name == signup_data["name"]
        assert got.bio == signup_data["bio"]
        assert got.email == signup_data["email"]
        assert got.telegram == f'https://t.me/{signup_data["telegram"][1:]}'
        assert got.instagram == f'https://instagram.com/{signup_data["instagram"]}'
        assert got.twitter == f'https://x.com/@{signup_data["twitter"][1:]}'

    def test_signup_duplicate(self, client):
        client.post(self.url, json=simple_signup_data)
        response = client.post(self.url, json=simple_signup_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.BAD_REQUEST.description
        assert message == f"username: {username!r} already exists!"


class TestLogin(BaseTest):
    url = base_url + "/login"

    def test_user_not_found_error(self, client):
        response = client.post(self.url, json=login_data)
        assert response.status_code == HTTPStatus.NOT_FOUND.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.NOT_FOUND.description
        assert message == f"<User:{username!r}> is not found!"

    def test_wrong_credentials(self, client, signup_mahdi):
        response = client.post(
            self.url, json={"username": "mahdi", "password": "12345677"}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.UNAUTHORIZED.description
        assert message == CredentialsError().message

    def test_login(self, client, signup_mahdi):
        response = client.post(self.url, json=login_data)
        assert response.status_code == 200, response.text

        refresh_token = response.cookies.get("Refresh-Token")
        x_csrf_token = response.headers.get("x-csrf-token")

        assert refresh_token is not None
        assert x_csrf_token is not None

        refresh_token_nt = decode_refresh_token(refresh_token)
        assert refresh_token_nt.username == username

        csrf_token = decode_csrf_token(x_csrf_token)
        assert csrf_token.refresh_token == refresh_token
        assert csrf_token.access_token is None


class TestQrImg(BaseTest, RefreshTokenMixin):
    url = base_url + "/2fa-img"

    def test_gen(self, client, login_mahdi):
        response = client.post(
            self.url,
            headers=self.make_auth_headers(login_mahdi.csrf_token),
            cookies=self.make_auth_cookies(login_mahdi.refresh_token),
        )
        assert response.status_code == 200, response.text

        img = response.text
        assert f'"{base64.b64encode(base64.b64decode(img)).decode()}"' == img


class TestVerify(BaseTest, RefreshTokenMixin):
    url = base_url + "/verify"

    def test_invalid_totp(self, client, login_mahdi):
        response = client.post(
            self.url,
            params={"code": "111111"},
            headers=self.make_auth_headers(login_mahdi.csrf_token),
            cookies=self.make_auth_cookies(login_mahdi.refresh_token),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.UNAUTHORIZED.description
        assert message == "Invalid TOTP code"

    def test_verify(self, client, login_mahdi, get_mahdi_totp_hash):
        totp_hash = get_mahdi_totp_hash
        uri = totp.TOTP(totp_hash)
        current = uri.now()

        response = client.post(
            self.url,
            params={"code": str(current)},
            headers=self.make_auth_headers(login_mahdi.csrf_token),
            cookies=self.make_auth_cookies(login_mahdi.refresh_token),
        )
        assert response.status_code == 200, response.text

        def get():
            async def _get():
                rd = await get_redis_client_mock()
                return await rd.get(sha256_username("mahdi"))

            return asyncio.run(_get())

        assert get() is True


class TestRefresh(BaseTest, RefreshTokenMixin):
    url = base_url + "/refresh"

    def test_not_2_step_verified(self, client, login_mahdi):
        response = client.post(
            self.url,
            headers=self.make_auth_headers(login_mahdi.csrf_token),
            cookies=self.make_auth_cookies(login_mahdi.refresh_token),
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.UNAUTHORIZED.description
        assert message == "Please verify 2 step verification first"

    def test_once(self, client, verified_mahdi):
        response = client.post(
            self.url,
            headers=self.make_auth_headers(verified_mahdi.csrf_token),
            cookies=self.make_auth_cookies(verified_mahdi.refresh_token),
        )
        assert response.status_code == 200, response.text

        refresh_token = response.cookies.get("Refresh-Token")
        access_token = response.cookies.get("Access-Token")
        x_csrf_token = response.headers.get("x-csrf-token")

        assert refresh_token is not None
        assert access_token is not None
        assert x_csrf_token is not None

        refresh_token_nt = decode_refresh_token(refresh_token)
        assert refresh_token_nt.username == username

        access_token_nt = decode_access_token(access_token)
        assert access_token_nt.username == username
        assert access_token_nt.role == UserRolesEnum.USER.value

        csrf_token = decode_csrf_token(x_csrf_token)
        assert csrf_token.refresh_token == refresh_token
        assert csrf_token.access_token == access_token

    def test_twice(self, client, verified_mahdi):
        response = client.post(
            self.url,
            headers=self.make_auth_headers(verified_mahdi.csrf_token),
            cookies=self.make_auth_cookies(verified_mahdi.refresh_token),
        )
        refresh_token = response.cookies.get("Refresh-Token")
        x_csrf_token = response.headers.get("x-csrf-token")

        response = client.post(
            self.url,
            headers=self.make_auth_headers(x_csrf_token),
            cookies=self.make_auth_cookies(refresh_token),
        )

        assert response.status_code == 200, response.text

        refresh_token = response.cookies.get("Refresh-Token")
        access_token = response.cookies.get("Access-Token")
        x_csrf_token = response.headers.get("x-csrf-token")

        assert refresh_token is not None
        assert access_token is not None
        assert x_csrf_token is not None

        refresh_token_nt = decode_refresh_token(refresh_token)
        assert refresh_token_nt.username == username

        access_token_nt = decode_access_token(access_token)
        assert access_token_nt.username == username
        assert access_token_nt.role == UserRolesEnum.USER.value

        csrf_token = decode_csrf_token(x_csrf_token)
        assert csrf_token.refresh_token == refresh_token
        assert csrf_token.access_token == access_token


class TestLogout(BaseTest):
    url = base_url + "/logout"

    def test_not_pass_access_token(self, client, login_mahdi):
        response = client.post(
            self.url,
            headers=self.make_auth_headers(login_mahdi.csrf_token),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.FORBIDDEN.description
        assert message == "Access-Token is not provided"

    def test_not_invalid_access_token(self, client, refreshed_mahdi):
        invalid_access_token = refreshed_mahdi.access_token.translate(
            str.maketrans({"a": "b"})
        )
        response = client.post(
            self.url,
            headers=self.make_auth_headers(refreshed_mahdi.csrf_token),
            cookies={"Access-Token": invalid_access_token},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.UNAUTHORIZED.description
        assert message == "Could not validate credentials"

    def test_logout(self, client, refreshed_mahdi):
        response = client.post(
            self.url,
            headers=self.make_auth_headers(refreshed_mahdi.csrf_token),
            cookies=self.make_auth_cookies(
                refreshed_mahdi.refresh_token, refreshed_mahdi.access_token
            ),
        )
        assert response.status_code == 200, response.text

        refresh_token = response.cookies.get("Refresh-Token")
        access_token = response.cookies.get("Access-Token")

        assert refresh_token == '""'
        assert access_token == '""'

        def get():
            async def _get():
                rd = await get_redis_client_mock()
                ref_ = await rd.get(refreshed_mahdi.refresh_token)
                sha_ = await rd.get(sha256_username("mahdi"))
                return ref_, sha_

            return asyncio.run(_get())

        ref, sha = get()
        assert ref is sha is None


class TestAccessToken(BaseTest):
    url = f"{settings.PREFIX}/{APIPrefixesEnum.USERS.value}/me"

    def test_not_pass_access_token(self, client, login_mahdi):
        response = client.get(
            self.url,
            headers=self.make_auth_headers(login_mahdi.csrf_token),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.FORBIDDEN.description
        assert message == "Access-Token is not provided"

    def test_not_invalid_access_token(self, client, refreshed_mahdi):
        invalid_access_token = refreshed_mahdi.access_token.translate(
            str.maketrans({"a": "b"})
        )
        response = client.get(
            self.url,
            headers=self.make_auth_headers(refreshed_mahdi.csrf_token),
            cookies={"Access-Token": invalid_access_token},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED.value, response.text

        code_message, message = self.extract_error_message(response.json())
        assert code_message == HTTPStatus.UNAUTHORIZED.description
        assert message == "Could not validate credentials"

    def test_me(self, client, refreshed_mahdi):
        response = client.get(
            self.url,
            headers=self.make_auth_headers(refreshed_mahdi.csrf_token),
            cookies={"Access-Token": refreshed_mahdi.access_token},
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == username
        for k, v in data.items():
            if k in ["username", "qr_img"]:
                continue
            assert v is None
