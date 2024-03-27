import asyncio
import base64
import io

import qrcode
from pyotp import random_base32, totp

from src.core.config import settings
from src.core.enums import UserRolesEnum
from src.core.exceptions import (
    DuplicateUsernameError,
    CredentialsError,
)
from src.core.schemas import (
    UserSchema,
    UserSignupSchema,
    UserOutSchema,
    UserLoginSchema,
)
from src.core.security import (
    hash_password,
    verify_password,
    encode_refresh_token,
    encode_csrf_token,
    encode_access_token,
    Token,
)
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

        provisioning_uri = totp.TOTP(user_schema.totp_hash).provisioning_uri(
            name=user_schema.username, issuer_name="SimpleRESTBlog"
        )
        buffered = io.BytesIO()
        qrcode.make(provisioning_uri).save(buffered)

        return UserOutSchema(
            **user_schema.model_dump(),
            qr_img=base64.b64encode(buffered.getvalue()).decode(),
        )

    async def authenticate(self, username: str, password: str) -> UserSchema:
        user = await self.repo.get(username)
        if verify_password(password, user.password):
            return user
        raise CredentialsError()

    async def get_user(self, username: str):
        return await self.repo.get(username)

    async def login_user(self, user_login: UserLoginSchema) -> Token:
        user = await self.repo.get(user_login.username)

        refresh_token = encode_refresh_token(user.username)
        csrf_token = encode_csrf_token(refresh_token)

        await self.redis_client.set(
            refresh_token,
            user.username,
            timeout=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )
        return Token(
            access_token=None,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )

    async def verify(self, refresh_token: str, username: str, code: str):
        in_cache_username = await self.redis_client.get(refresh_token, None)
        if in_cache_username is None or in_cache_username != username:
            raise CredentialsError("Invalid Refresh-Token")

        user = await self.repo.get(username)
        if not totp.TOTP(user.totp_hash).verify(code):
            raise CredentialsError("Invalid TOTP code")

        await self.redis_client.set(
            username, True, timeout=settings.TFA_EXPIRE_MINUTES * 60
        )

    async def refresh_token(self, old_refresh: str, username: str):
        in_cache_username, ref_ttl, verified = asyncio.gather(
            self.redis_client.get(old_refresh),
            self.redis_client.ttl(old_refresh),
            self.redis_client.get(username),
        )
        if in_cache_username is None or in_cache_username != username:
            raise CredentialsError("Invalid Refresh-Token")

        if not verified:
            raise CredentialsError("Please verify 2 step verification first")

        user = await self.repo.get(username)

        access_token = encode_access_token(username, user.role)
        ref_expire = ref_ttl // 60
        refresh_token = encode_refresh_token(username, ref_expire)
        csrf_token = encode_csrf_token(refresh_token, access_token)

        await asyncio.gather(
            self.redis_client.set(refresh_token, username, timeout=ref_expire),
            self.redis_client.delete(old_refresh),
        )
        return Token(access_token, refresh_token, csrf_token)

    async def logout(self, refresh_token: str, username: str):
        if refresh_token is None:
            raise CredentialsError("Refresh-Token is not provided")

        in_cache_username = await self.redis_client.get(refresh_token)
        if in_cache_username != username:
            raise CredentialsError("Invalid Refresh-Token")

        await self.redis_client.delete(refresh_token)
