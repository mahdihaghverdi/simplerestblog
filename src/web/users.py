from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.core.acl import get_permission_setting, ACLSetting, check_permission
from src.core.database import get_db_sessionmaker
from src.core.depends import get_current_user_from_db
from src.core.enums import RoutesEnum, APIPrefixesEnum
from src.core.schemas import (
    UserOutSchema,
    UserSchema,
)
from src.core.security import get_access_token, AccessToken
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService

router = APIRouter(prefix=f"/{APIPrefixesEnum.USERS.value}")


@router.get("/me", response_model=UserOutSchema, status_code=status.HTTP_200_OK)
async def me(user: Annotated[UserSchema, Depends(get_current_user_from_db)]):
    return user


@router.get("/{username}", response_model=UserOutSchema, status_code=status.HTTP_200_OK)
async def get_by_username(
    username: str,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    token: Annotated[AccessToken, Depends(get_access_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    await check_permission(
        session_maker=session_maker,
        user_role=token.role,
        username=token.username,
        resource_identifier=username,
        route=RoutesEnum.GET_USER_BY_USERNAME,
        permission_setting=permission_setting,
    )
    async with UnitOfWork(session_maker) as session:
        repo = UserRepo(session)
        service = UserService(repo)
        return await service.get_user(username)
