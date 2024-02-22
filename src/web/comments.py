from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.schemas import UserSchema, CreateCommentReplySchema, CommentReplySchema
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
