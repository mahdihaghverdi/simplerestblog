from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.core.acl import get_permission_setting, ACLSetting, check_permission
from src.core.database import get_db_sessionmaker
from src.core.depends import get_current_user_from_db
from src.core.enums import RoutesEnum, APIPrefixesEnum
from src.core.schemas import (
    UserSchema,
    CreateCommentReplySchema,
    CommentReplySchema,
)
from src.repository.comment_repo import CommentReplyRepo
from src.repository.unitofwork import UnitOfWork
from src.service.comment_service import CommentReplyService

router = APIRouter(prefix=f"/{APIPrefixesEnum.COMMENTS.value}")


@router.post(
    "/{post_id}", response_model=CommentReplySchema, status_code=status.HTTP_201_CREATED
)
async def add_comment(
    post_id: int,
    comment: CreateCommentReplySchema,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = CommentReplyRepo(session)
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
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = CommentReplyRepo(session)
        service = CommentReplyService(repo)
        reply = await service.create_reply(post_id, comment_id, reply, user.username)
    return reply


@router.get("/{post_id}", response_model=list[CommentReplySchema])
async def get_comments(
    post_id: int,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    page: Annotated[int, Query(ge=1)] = 1,
    how_many: Annotated[int, Query(ge=5, title="how-many")] = 5,
    order: Annotated[Literal["first", "last", "most_replied"], Query()] = "last",
):
    async with UnitOfWork(session_maker) as session:
        repo = CommentReplyRepo(session)
        service = CommentReplyService(repo)
        comments = await service.get_comments(post_id, page, how_many, order)
    return comments


@router.get("/{post_id}/{comment_id}", response_model=list[CommentReplySchema])
async def get_replies(
    post_id: int,
    comment_id: int,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    page: Annotated[int, Query(ge=1)] = 1,
    how_many: Annotated[int, Query(ge=5, title="how-many")] = 5,
    order: Annotated[Literal["first", "last", "most_replied"], Query()] = "last",
):
    async with UnitOfWork(session_maker) as session:
        repo = CommentReplyRepo(session)
        service = CommentReplyService(repo)
        comments = await service.get_replies(post_id, comment_id, page, how_many, order)
    return comments


@router.put("/{post_id}/{comment_id}", response_model=CommentReplySchema)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment: CreateCommentReplySchema,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = CommentReplyRepo(session)
        service = CommentReplyService(repo)
        comment = await service.update_comment(
            post_id, comment_id, comment, user.username
        )
    return comment


@router.delete("/{post_id}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: int,
    comment_id: int,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    async with UnitOfWork(session_maker) as session:
        await check_permission(
            session=session,
            user=user,
            resource_identifier=comment_id,
            route=RoutesEnum.DELETE_COMMENT,
            permission_setting=permission_setting,
        )
        repo = CommentReplyRepo(session)
        service = CommentReplyService(repo)
        await service.delete_comment(post_id, comment_id)
