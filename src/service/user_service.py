import base64
import io
from typing import Annotated

import qrcode
from fastapi import Depends
from pyotp import random_base32, totp
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.enums import UserRolesEnum
from src.core.exceptions import (
    DuplicateUsernameError,
    DatabaseConnectionError,
    CredentialsError,
)
from src.core.schemas import (
    UserSchema,
    AccessTokenData,
    UserSignupSchema,
    UserOutSchema,
    Token,
    UserLoginSchema,
)
from src.core.security import (
    hash_password,
    validate_token,
    verify_password,
    create_refresh_token,
    create_csrf_token,
)
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service import Service


async def get_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token_data: Annotated[AccessTokenData, Depends(validate_token)],
) -> UserSchema:
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        user = await service.get_user(token_data.username)
    return user


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
        if not bool(self.redis_client):
            raise DatabaseConnectionError("Redis connection is not initialized")

        user = await self.repo.get(user_login.username)

        refresh_token = create_refresh_token(user.username)
        csrf_token = create_csrf_token(refresh_token)

        await self.redis_client.set(
            refresh_token, user.username, timeout=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        return Token(
            access_token=None,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )
