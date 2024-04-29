from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.core.acl import check_permission, ACLSetting, get_permission_setting
from src.core.database import get_db_sessionmaker
from src.core.depends import get_current_user_from_db, get_tokens_from_cookies
from src.core.enums import APIPrefixesEnum, RoutesEnum
from src.core.schemas import LittlePostSchema, UserSchema
from src.repository.post_repo import PostRepo
from src.repository.unitofwork import UnitOfWork
from src.service.post_service import PostService

router = APIRouter(prefix=f"/{APIPrefixesEnum.POSTS.value}")


@router.get("/", response_model=list[LittlePostSchema])
async def get_self_posts(
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = PostRepo(session)
        service = PostService(repo)
        posts = await service.get_all_posts(user.username)
    return posts


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


@router.post("/unpublish/{post_id}", response_class=RedirectResponse)
async def unpublish_post(
    request: Request,
    post_id: int,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
    tokens: Annotated[str, Depends(get_tokens_from_cookies)],
):
    async with UnitOfWork(session_maker) as session:
        await check_permission(
            session, user, post_id, RoutesEnum.UNPUBLISH_POST, permission_setting
        )
        repo = PostRepo(session)
        service = PostService(repo)
        draft_url = await service.unpublish_post(post_id)

    rr = RedirectResponse(
        url=f"{request.base_url}{draft_url}",
        status_code=303,
        headers={"X-CSRF-TOKEN": tokens[1]},
    )
    rr.set_cookie(
        key="Access-Token",
        value=tokens[0],
        httponly=True,
        samesite="strict",
    )
    return rr
