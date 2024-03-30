from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.core.database import get_db_sessionmaker
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
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
):
    async with UnitOfWork(session_maker) as session:
        repo = PostRepo(session)
        service = PostService(repo)
        post = await service.get_global_post(username, link)
    return post
