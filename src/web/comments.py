from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.schemas import UserSchema, CreateCommentSchema, CommentSchema
from src.repository.comment_repo import CommentRepo
from src.repository.unitofwork import UnitOfWork
from src.service.comment_service import CommentService
from src.service.user_service import get_user

router = APIRouter(prefix="/comments")


@router.post(
    "/{post_id}", response_model=CommentSchema, status_code=status.HTTP_201_CREATED
)
async def add_comment(
    post_id: int,
    comment: CreateCommentSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = CommentRepo(db)
        service = CommentService(repo)
        comment = await service.create_comment(post_id, comment, user.username)
    return comment
