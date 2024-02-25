from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.enums import APIPrefixesEnum
from src.core.schemas import LittlePostSchema
from src.repository.post_repo import PostRepo
from src.repository.unitofwork import UnitOfWork
from src.service.post_service import PostService

router = APIRouter(prefix=f"/{APIPrefixesEnum.POSTS.value}")


@router.get("/{username}", response_model=list[LittlePostSchema])
async def get_posts(username: str, db: Annotated[AsyncSession, Depends(get_db)]):
    async with UnitOfWork(db):
        repo = PostRepo(db)
        service = PostService(repo)
        posts = await service.get_all_posts(username)
    return posts
