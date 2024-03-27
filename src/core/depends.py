from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from src.core.exceptions import ForbiddenException, CredentialsError
from src.core.security import decode_refresh_token, decode_csrf_token, decode_access_token

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
