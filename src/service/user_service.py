from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.enums import UserRolesEnum
from src.core.exceptions import (
    DuplicateUsernameError,
    CredentialsError,
    UserNotFoundError,
)
from src.core.schemas import UserSchema, TokenData, UserSignupSchema
from src.core.security import hash_password, validate_token
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service import Service


async def get_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token_data: Annotated[TokenData, Depends(validate_token)],
) -> UserSchema:
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        user = await service.get_user(token_data.username)
    return user


class UserService(Service[UserRepo]):
    async def signup_user(self, user_data: UserSignupSchema) -> UserSchema:
        user_data.password = hash_password(user_data.password)
        if user_data.telegram is not None:
            user_data.telegram = f"https://t.me/{user_data.telegram}"
        if user_data.instagram is not None:
            user_data.instagram = f"https://instagram.com/{user_data.instagram}"
        if user_data.twitter is not None:
            user_data.twitter = f"https://x.com/@{user_data.twitter}"

        user = user_data.model_dump()
        user["role"] = UserRolesEnum.USER.value
        user = await self.repo.add(user)
        if user is None:
            raise DuplicateUsernameError(user_data.username)
        return user

    async def authenticate(self, username: str, password: str) -> UserSchema:
        user = await self.repo.auth(username, password)
        if user is None:
            raise CredentialsError()
        return user

    async def get_user(self, username: str):
        user = await self.repo.get(username)
        if user is None:
            raise UserNotFoundError(username)
        return user
