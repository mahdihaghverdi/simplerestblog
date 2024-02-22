from datetime import datetime
from typing import Annotated, TypeAlias

import slugify
from pydantic import BaseModel, EmailStr, constr, AfterValidator, conset

from src.core.enums import UserRolesEnum, APIMethodsEnum


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


LinkTupleType: TypeAlias = tuple[APIMethodsEnum, str] | None


class LittleDraftSchema(BaseModel):
    id: int
    title: str
    updated: datetime | None
    link: LinkTupleType


class DraftSchema(BaseModel):
    id: int
    title: str
    body: str
    created: datetime
    updated: datetime | None
    username: str
    draft_hash: str


class CreateDraftSchema(BaseModel):
    title: str
    body: str


class UpdateDraftSchema(BaseModel):
    title: str
    body: str


def _slugify(slug) -> str:
    return slugify.slugify(slug)


Slug = Annotated[
    constr(strip_whitespace=True, to_lower=True, min_length=1),
    AfterValidator(_slugify),
]


class PublishDraftSchema(BaseModel):
    tags: conset(
        constr(strip_whitespace=True, to_lower=True, min_length=1),
        min_length=1,
        max_length=5,
    )
    slug: Slug


class PostSchema(BaseModel):
    id: int
    title: str
    body: str
    tags: set[str]
    published: datetime
    updated: datetime | None = None
    comments_count: int


class CreateCommentReplySchema(BaseModel):
    comment: constr(strip_whitespace=True, min_length=1, max_length=256)


class CommentReplySchema(BaseModel):
    id: int
    commented: datetime
    comment: str
    path: str | None = None
    updated: datetime | None = None
    parent_id: int | None = None
    username: str


class LittlePostSchema(BaseModel):
    id: int
    title: str
    slug: str
    published: datetime
