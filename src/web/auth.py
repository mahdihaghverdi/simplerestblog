from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from src.core.database import get_db
from src.core.depends import (
    get_current_username_with_refresh,
    get_current_username_with_access,
)
from src.core.enums import APIPrefixesEnum
from src.core.redis_db import RedisClient, get_redis_client
from src.core.schemas import UserLoginSchema
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService

router = APIRouter(prefix=f"/{APIPrefixesEnum.AUTH.value}")


@router.post("/login")
async def login(
    response: Response,
    user_login: UserLoginSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
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


@router.post("/2fa-img")
async def get_2fa_image(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
    username: Annotated[str, Depends(get_current_username_with_refresh)],
) -> str:
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo, redis_client)
        qr_img = await service.get_user_qr_img(
            request.cookies.get("Refresh-Token"), username
        )
    return qr_img


@router.post("/verify")
async def verify(
    request: Request,
    code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
    username: Annotated[str, Depends(get_current_username_with_refresh)],
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo, redis_client)
        await service.verify(
            refresh_token=request.cookies.get("Refresh-Token"),
            username=username,
            code=code,
        )


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
    username: Annotated[str, Depends(get_current_username_with_refresh)],
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo, redis_client)
        tokens = await service.refresh_token(
            request.cookies.get("Refresh-Token"), username
        )

    response.set_cookie(
        key="Refresh-Token",
        value=tokens.refresh_token,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    response.set_cookie(
        key="Access-Token",
        value=tokens.access_token,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    response.headers["X-CSRF-TOKEN"] = tokens.csrf_token


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
    username: Annotated[str, Depends(get_current_username_with_access)],
):
    service = UserService(repo=None, redis_client=redis_client)
    await service.logout(request.cookies.get("Refresh-Token"), username)

    response.set_cookie(
        key="Refresh-Token",
        value="",
        secure=True,
        httponly=True,
        samesite="strict",
    )
    response.set_cookie(
        key="Access-Token",
        value="",
        secure=True,
        httponly=True,
        samesite="strict",
    )
