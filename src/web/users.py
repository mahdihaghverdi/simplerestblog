from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from src.core.acl import get_permission_setting, ACLSetting, check_permission
from src.core.database import get_db
from src.core.enums import RoutesEnum, APIPrefixesEnum
from src.core.redis_db import get_redis_db, RedisClient
from src.core.schemas import (
    UserOutSchema,
    UserSignupSchema,
    UserSchema,
    AccessTokenData,
    UserLoginSchema,
)
from src.core.security import validate_token
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService, get_user

router = APIRouter(prefix=f"/{APIPrefixesEnum.USERS.value}")


@router.post(
    "/signup",
    response_model=UserOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_data: UserSignupSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        user = await service.signup_user(user_data)
    return user


@router.post("/login")
async def login(
    response: Response,
    user_login: UserLoginSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[RedisClient, Depends(get_redis_db)],
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo, redis_client)
        tokens = await service.login_user(user_login)

    response.set_cookie(
        key="Refresh-Token",
        value=tokens.refresh_token,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    response.headers["X-CSRF-TOKEN"] = tokens.csrf_token


@router.get("/me", response_model=UserOutSchema, status_code=status.HTTP_200_OK)
async def me(user: Annotated[UserSchema, Depends(get_user)]):
    return user


@router.get("/{username}", response_model=UserOutSchema, status_code=status.HTTP_200_OK)
async def get_by_username(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[AccessTokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    await check_permission(
        db=db,
        user_role=token.role,
        username=token.username,
        resource_identifier=username,
        route=RoutesEnum.GET_USER_BY_USERNAME,
        permission_setting=permission_setting,
    )
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        return await service.get_user(username)
