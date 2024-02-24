from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.acl import get_permission_setting, ACLSetting, check_permission
from src.core.database import get_db
from src.core.enums import RoutesEnum
from src.core.schemas import (
    UserSchema,
    CreateCommentReplySchema,
    CommentReplySchema,
    TokenData,
)
from src.core.security import validate_token
from src.repository.comment_repo import CommentReplyRepo
from src.repository.unitofwork import UnitOfWork
from src.service.comment_service import CommentReplyService
from src.service.user_service import get_user

router = APIRouter(prefix="/comments")


@router.post(
    "/{post_id}", response_model=CommentReplySchema, status_code=status.HTTP_201_CREATED
)
async def add_comment(
    post_id: int,
    comment: CreateCommentReplySchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = CommentReplyRepo(db)
        service = CommentReplyService(repo)
        comment = await service.create_comment(post_id, comment, user.username)
    return comment


@router.post(
    "/{post_id}/{comment_id}",
    response_model=CommentReplySchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_reply(
    post_id: int,
    comment_id: int,
    reply: CreateCommentReplySchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = CommentReplyRepo(db)
        service = CommentReplyService(repo)
        reply = await service.create_reply(post_id, comment_id, reply, user.username)
    return reply


@router.get("/{post_id}", response_model=list[CommentReplySchema])
async def get_comments(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    how_many: Annotated[int, Query(ge=5, title="how-many")] = 5,
    order: Annotated[Literal["first", "last", "most_replied"], Query()] = "last",
):
    async with UnitOfWork(db):
        repo = CommentReplyRepo(db)
        service = CommentReplyService(repo)
        comments = await service.get_comments(post_id, page, how_many, order)
    return comments


@router.get("/{post_id}/{comment_id}", response_model=list[CommentReplySchema])
async def get_replies(
    post_id: int,
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    how_many: Annotated[int, Query(ge=5, title="how-many")] = 5,
    order: Annotated[Literal["first", "last", "most_replied"], Query()] = "last",
):
    async with UnitOfWork(db):
        repo = CommentReplyRepo(db)
        service = CommentReplyService(repo)
        comments = await service.get_replies(post_id, comment_id, page, how_many, order)
    return comments


@router.put("/{post_id}/{comment_id}", response_model=CommentReplySchema)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment: CreateCommentReplySchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = CommentReplyRepo(db)
        service = CommentReplyService(repo)
        comment = await service.update_comment(
            post_id, comment_id, comment, user.username
        )
    return comment


@router.delete("/{post_id}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: int,
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    await check_permission(
        db=db,
        user_role=token.role,
        username=token.username,
        resource_identifier=comment_id,
        route=RoutesEnum.DELETE_COMMENT,
        permission_setting=permission_setting,
    )
    async with UnitOfWork(db):
        repo = CommentReplyRepo(db)
        service = CommentReplyService(repo)
        await service.delete_comment(post_id, comment_id)
