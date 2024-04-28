from datetime import datetime, timedelta
from typing import NamedTuple
from zoneinfo import ZoneInfo

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from starlette.requests import Request

from src.core.config import settings
from src.core.enums import UserRolesEnum
from src.core.exceptions import CredentialsError


class RefreshToken(NamedTuple):
    username: str


class CSRFToken(NamedTuple):
    refresh_token: str
    access_token: str | None


class AccessToken(NamedTuple):
    username: str
    role: UserRolesEnum


class Token(NamedTuple):
    access_token: str | None
    refresh_token: str
    csrf_token: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def encode_refresh_token(
    username: str, expire=settings.SRB_REFRESH_TOKEN_EXPIRE_MINUTES
) -> str:
    to_encode = {"sub": "refresh_token", "username": username}
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(minutes=expire)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode, settings.SRB_SECRET_KEY, algorithm=settings.SRB_ALGORITHM
    )
    return encoded_jwt


def decode_refresh_token(token) -> RefreshToken:
    try:
        token_payload = jwt.decode(
            token, settings.SRB_SECRET_KEY, algorithms=[settings.SRB_ALGORITHM]
        )
    except InvalidTokenError:
        raise CredentialsError("Invalid Refresh-Token") from None
    else:
        sub, username = token_payload.get("sub"), token_payload.get("username")
        if (sub is None) or (not sub == "refresh_token") or (username is None):
            raise CredentialsError("Invalid Refresh-Token")
        return RefreshToken(username=username)


def encode_csrf_token(refresh_token, access_token=None) -> str:
    to_encode = {"sub": "csrf_token", "refresh_token": refresh_token}
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.SRB_REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    to_encode["exp"] = expire
    to_encode["access_token"] = access_token
    encoded_jwt = jwt.encode(
        to_encode, settings.SRB_SECRET_KEY, algorithm=settings.SRB_ALGORITHM
    )
    return encoded_jwt


def decode_csrf_token(token) -> CSRFToken:
    try:
        token_payload = jwt.decode(
            token, settings.SRB_SECRET_KEY, algorithms=[settings.SRB_ALGORITHM]
        )
    except InvalidTokenError:
        raise CredentialsError() from None
    else:
        sub, refresh_token, access_token = (
            token_payload.get("sub"),
            token_payload.get("refresh_token"),
            token_payload.get("access_token"),
        )
        if (sub is None) or (not sub == "csrf_token") or (refresh_token is None):
            raise CredentialsError("Invalid CSRF-Token")
        return CSRFToken(refresh_token=refresh_token, access_token=access_token)


def encode_access_token(username: str, role: UserRolesEnum, refresh_token: str) -> str:
    to_encode = {"username": username, "role": role, "refresh_token": refresh_token}
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.SRB_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode, settings.SRB_SECRET_KEY, algorithm=settings.SRB_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token) -> AccessToken:
    try:
        payload = jwt.decode(
            token, settings.SRB_SECRET_KEY, algorithms=[settings.SRB_ALGORITHM]
        )
    except InvalidTokenError:
        raise CredentialsError()
    else:
        username, role = payload.get("username"), payload.get("role")
        if username is None or role is None:
            raise CredentialsError()
    return AccessToken(username=username, role=role)


def get_access_token(request: Request) -> AccessToken:
    token = request.cookies.get("Access-Token")
    if token is None:
        raise CredentialsError("Access-Token is not provided")
    token_data = decode_access_token(token)
    return token_data
