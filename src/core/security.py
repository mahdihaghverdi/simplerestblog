from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext

from src.core.config import settings
from src.core.exceptions import CredentialsError
from src.core.schemas import AccessTokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.PREFIX}/auth/access-token",
)


def create_refresh_token(username: str) -> str:
    to_encode = {"sub": "refresh_token", "username": username}
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_csrf_token(refresh_token) -> str:
    to_encode = {"sub": "csrf_token", "refresh_token": refresh_token}
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_access_token(data: AccessTokenData) -> str:
    to_encode = data.model_dump()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_jwt(token) -> AccessTokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except InvalidTokenError:
        raise CredentialsError()
    else:
        username = payload.get("username")
        role = payload.get("role")
        if username is None:
            raise CredentialsError()
        if role is None:
            raise CredentialsError()

    return AccessTokenData(username=username, role=role)


def validate_token(token: Annotated[str, Depends(oauth2_scheme)]) -> AccessTokenData:
    token_data = decode_jwt(token)
    return token_data
