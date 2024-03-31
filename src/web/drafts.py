from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.core.acl import get_permission_setting, ACLSetting, check_permission
from src.core.database import get_db_sessionmaker
from src.core.depends import get_current_user_from_db
from src.core.enums import RoutesEnum, APIPrefixesEnum
from src.core.schemas import (
    LittleDraftSchema,
    UserSchema,
    DraftSchema,
    CreateDraftSchema,
    UpdateDraftSchema,
    PublishDraftSchema,
)
from src.repository.draft_repo import DraftRepo
from src.repository.post_repo import PostRepo
from src.repository.unitofwork import UnitOfWork
from src.service.draft_service import DraftService
from src.service.post_service import PostService

router = APIRouter(prefix=f"/{APIPrefixesEnum.DRAFTS.value}")


@router.post("/", response_model=DraftSchema, status_code=status.HTTP_201_CREATED)
async def create_draft(
    draft: CreateDraftSchema,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = DraftRepo(session)
        service = DraftService(repo)
        draft = await service.create_draft(user.username, draft)
    return draft


@router.get(
    "/all",
    response_model=list[LittleDraftSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_drafts(
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
    desc_order: Annotated[bool, Query(description="DESC if True ASC otherwise.")] = True,
):
    async with UnitOfWork(session_maker) as session:
        repo = DraftRepo(session)
        service = DraftService(repo)
        drafts = await service.get_all(user.username, desc_order)
    return drafts


@router.get(
    "/all/{username}",
    response_model=list[LittleDraftSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_drafts_by_username(
    username: str,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
    desc_order: Annotated[bool, Query(description="DESC if True ASC otherwise.")] = True,
):
    async with UnitOfWork(session_maker) as session:
        await check_permission(
            session,
            user,
            username,
            RoutesEnum.GET_ALL_DRAFTS_BY_USERNAME,
            permission_setting,
        )
        repo = DraftRepo(session)
        service = DraftService(repo)
        drafts = await service.get_all(username, desc_order)
    return drafts


@router.get("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def get_one_draft(
    draft_id: int,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = DraftRepo(session)
        service = DraftService(repo)
        draft = await service.get_one(draft_id, user.username)
    return draft


@router.get(
    "/{username}/{draft_id}",
    response_model=DraftSchema,
    status_code=status.HTTP_200_OK,
)
async def get_one_draft_by_username(
    username: str,
    draft_id: int,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    async with UnitOfWork(session_maker) as session:
        await check_permission(
            session,
            user,
            draft_id,
            RoutesEnum.GET_ONE_DRAFT_BY_USERNAME,
            permission_setting,
        )
        repo = DraftRepo(session)
        service = DraftService(repo)
        draft = await service.get_one(draft_id, username)
    return draft


@router.put("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def update_draft(
    draft_id: int,
    draft: UpdateDraftSchema,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = DraftRepo(session)
        service = DraftService(repo)
        draft = await service.update_draft(draft_id, draft, user.username)
    return draft


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: int,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = DraftRepo(session)
        service = DraftService(repo)
        await service.delete_draft(draft_id, user.username)


@router.get(
    "/open-read/@{username}/{slug}",
    response_model=DraftSchema,
    status_code=status.HTTP_200_OK,
)
async def open_read(
    username: str,
    slug: str,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
):
    async with UnitOfWork(session_maker) as session:
        repo = DraftRepo(session)
        service = DraftService(repo)
        draft = await service.get_global(username, slug)
    return draft


@router.post(
    "/publish/{draft_id}",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
)
async def publish_draft(
    reqeust: Request,
    draft_id: int,
    post: PublishDraftSchema,
    session_maker: Annotated[async_sessionmaker, Depends(get_db_sessionmaker)],
    user: Annotated[UserSchema, Depends(get_current_user_from_db)],
):
    async with UnitOfWork(session_maker) as session:
        repo = PostRepo(session)
        service = PostService(repo)
        link = await service.create_post(draft_id, post, user.username)
    return f"{str(reqeust.base_url)}@{user.username}/{link}"
