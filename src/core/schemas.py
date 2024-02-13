from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, constr, AfterValidator

from src.core.enums import UserRolesEnum


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
    role: UserRolesEnum


class UserOutSchema(_UserSchema):
    telegram: str | None = None
    instagram: str | None = None
    twitter: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    role: UserRolesEnum | None = None
    username: str | None = None


class LittleDraftSchema(BaseModel):
    id: int
    title: str
    updated: datetime


class DraftSchema(BaseModel):
    id: str
    title: str
    body: str
    created: datetime
    updated: datetime
    username: str


class CreateDraftSchema(BaseModel):
    title: str
    body: str


class UpdateDraftSchema(BaseModel):
    title: str
    body: str
