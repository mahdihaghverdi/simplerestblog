from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.core.database import get_db_sessionmaker
from src.core.enums import APIPrefixesEnum
from src.core.schemas import LittlePostSchema
from src.repository.post_repo import PostRepo
from src.repository.unitofwork import UnitOfWork
from src.service.post_service import PostService

router = APIRouter(prefix=f"/{APIPrefixesEnum.POSTS.value}")


@router.get("/{username}", response_model=list[LittlePostSchema])
async def get_posts(
    username: str,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
):
    async with UnitOfWork(session_maker) as session:
        repo = PostRepo(session)
        service = PostService(repo)
        posts = await service.get_all_posts(username)
    return posts
