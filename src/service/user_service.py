import asyncio

from pyotp import random_base32, totp

from src.core.config import settings
from src.core.enums import UserRolesEnum
from src.core.exceptions import (
    DuplicateUsernameError,
    CredentialsError,
    ForbiddenError,
)
from src.core.schemas import (
    UserSignupSchema,
    UserOutSchema,
    UserLoginSchema,
    UserRegisterOutSchema,
)
from src.core.security import (
    hash_password,
    verify_password,
    encode_refresh_token,
    encode_csrf_token,
    encode_access_token,
    Token,
)
from src.core.utils import create_totp_qr_img, sha256_username
from src.repository.user_repo import UserRepo
from src.service import Service


class UserService(Service[UserRepo]):
    async def signup_user(self, user_data: UserSignupSchema) -> UserOutSchema:
        if await self.repo.username_exists(user_data.username):
            raise DuplicateUsernameError(user_data.username)

        user_data.password = hash_password(user_data.password)

        if user_data.telegram is not None:
            user_data.telegram = f"https://t.me/{user_data.telegram}"
        if user_data.instagram is not None:
            user_data.instagram = f"https://instagram.com/{user_data.instagram}"
        if user_data.twitter is not None:
            user_data.twitter = f"https://x.com/@{user_data.twitter}"

        user = user_data.model_dump()
        user["role"] = UserRolesEnum.USER.value
        user["totp_hash"] = str(random_base32())
        user_schema = await self.repo.add(user)

        qr_img = create_totp_qr_img(user_schema)

        return UserRegisterOutSchema(
            **user_schema.model_dump(),
            qr_img=qr_img,
        )

    async def get_user(self, username: str):
        return await self.repo.get(username)

    async def login_user(self, user_login: UserLoginSchema) -> Token:
        user = await self.repo.get(user_login.username)

        if not verify_password(user_login.password, user.password):
            raise CredentialsError()

        refresh_token = encode_refresh_token(user.username)
        csrf_token = encode_csrf_token(refresh_token)

        await self.redis_client.set(
            refresh_token,
            user.username,
            timeout=settings.SRB_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )
        return Token(
            access_token=None,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )

    async def _check_refresh_token(self, refresh_token, username):
        if refresh_token is None:
            raise ForbiddenError("Refresh-Token is not provided")
        in_cache_username = await self.redis_client.get(refresh_token)
        if in_cache_username != username:
            raise CredentialsError("Invalid Refresh-Token")

    async def verify(self, refresh_token: str, username: str, code: str):
        await self._check_refresh_token(refresh_token, username)
        user = await self.repo.get(username)
        if not totp.TOTP(user.totp_hash).verify(code):
            raise CredentialsError("Invalid TOTP code")

        await self.redis_client.set(
            sha256_username(username), True, timeout=settings.SRB_TFA_EXPIRE_MINUTES * 60
        )

    async def refresh_token(self, old_refresh: str, username: str):
        if old_refresh is None:
            raise ForbiddenError("Refresh-Token is not provided")

        in_cache_username, ref_ttl, verified = await asyncio.gather(
            self.redis_client.get(old_refresh),
            self.redis_client.ttl(old_refresh),
            self.redis_client.get(sha256_username(username)),
        )
        if in_cache_username is None or in_cache_username != username:
            raise CredentialsError("Invalid Refresh-Token")

        if not verified:
            raise CredentialsError("Please verify 2 step verification first")

        user = await self.repo.get(username)

        ref_expire = ref_ttl // 60
        refresh_token = encode_refresh_token(username, ref_expire)
        access_token = encode_access_token(username, user.role, refresh_token)
        csrf_token = encode_csrf_token(refresh_token, access_token)

        await asyncio.gather(
            self.redis_client.set(refresh_token, username, timeout=ref_expire),
            self.redis_client.delete(old_refresh),
        )
        return Token(access_token, refresh_token, csrf_token)

    async def logout(self, refresh_token: str, username: str):
        await self._check_refresh_token(refresh_token, username)
        await asyncio.gather(
            self.redis_client.delete(refresh_token),
            self.redis_client.delete(sha256_username(username)),
        )

    async def get_user_qr_img(self, refresh_token: str, username: str):
        await self._check_refresh_token(refresh_token, username)
        user = await self.repo.get(username)
        return create_totp_qr_img(user)
