from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.core.database import get_db
from src.core.exceptions import ForbiddenException, CredentialsError
from src.core.security import decode_refresh_token, decode_csrf_token, decode_access_token
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService

http_bearer = HTTPBearer()


async def get_current_username_with_refresh(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
):
    if credentials.scheme != "Bearer":
        raise ForbiddenException("Invalid Header")

    refresh_token = request.cookies.get("Refresh-Token")
    if not refresh_token:
        raise ForbiddenException("Refresh-Token is not provided")

    refresh_token = decode_refresh_token(refresh_token)
    csrf_token = decode_csrf_token(credentials.credentials)
    if csrf_token.refresh_token != refresh_token:
        CredentialsError()

    return refresh_token.username


async def get_current_username_with_access(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
):
    if credentials.scheme != "Bearer":
        raise ForbiddenException("Invalid Header")

    access_token = request.cookies.get("Access-Token")
    if not access_token:
        raise ForbiddenException("Access-Token is not provided")

    access_token = decode_access_token(access_token)
    csrf_token = decode_csrf_token(credentials.credentials)
    if csrf_token.access_token != access_token:
        CredentialsError()

    return access_token.username


async def get_current_user_from_db(
    db: Annotated[AsyncSession, Depends(get_db)],
    username: Annotated[str, Depends(get_current_username_with_access)],
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        user = await service.get_user(username)
    return user
