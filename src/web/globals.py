from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db_session
from src.core.schemas import PostSchema
from src.repository.post_repo import PostRepo
from src.repository.unitofwork import UnitOfWork
from src.service.post_service import PostService

router = APIRouter()


@router.get(
    "/@{username}/{link}",
    response_model=PostSchema,
    status_code=status.HTTP_200_OK,
)
async def get_global(
    username: str,
    link: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    async with UnitOfWork(db):
        repo = PostRepo(db)
        service = PostService(repo)
        post = await service.get_global_post(username, link)
    return post
