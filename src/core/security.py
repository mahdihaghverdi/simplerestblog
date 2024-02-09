from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext

from src.core.config import settings
from src.core.exceptions import CredentialsException
from src.core.schemas import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/{settings.API_VERSION}/auth/access-token",
)


def create_access_token(data: TokenData) -> str:
    to_encode = data.model_dump()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_jwt(token) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise CredentialsException()
        return TokenData(username=username)
    except JWTError:
        raise CredentialsException()


def authenticate(token: str) -> TokenData:
    token_data = decode_jwt(token)
    return token_data
