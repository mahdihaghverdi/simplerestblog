from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, constr, AfterValidator


def remove_at_sign(str_id: str) -> str:
    # add @ if it is not present
    if not str_id.startswith("@"):
        return str_id
    return str_id[1:]


NoAtStr = Annotated[str, AfterValidator(remove_at_sign)]


class _UserSchema(BaseModel):
    username: constr(to_lower=True)
    name: str | None = None
    bio: str | None = None
    email: EmailStr | None = None
    telegram: NoAtStr | None = None
    instagram: NoAtStr | None = None
    twitter: NoAtStr | None = None


class UserSignupSchema(_UserSchema):
    password: constr(strip_whitespace=True, min_length=8)


class UserSchema(UserSignupSchema):
    created: datetime


class UserOutSchema(_UserSchema):
    telegram: str | None = None
    instagram: str | None = None
    twitter: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
