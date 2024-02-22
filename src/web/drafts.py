from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.core.acl import get_permission_setting, ACLSetting, check_permission
from src.core.database import get_db
from src.core.enums import RoutesEnum, APIPrefixesEnum
from src.core.schemas import (
    LittleDraftSchema,
    UserSchema,
    TokenData,
    DraftSchema,
    CreateDraftSchema,
    UpdateDraftSchema,
    PublishDraftSchema,
)
from src.core.security import validate_token
from src.repository.draft_repo import DraftRepo
from src.repository.post_repo import PostRepo
from src.repository.unitofwork import UnitOfWork
from src.service.draft_service import DraftService
from src.service.post_service import PostService
from src.service.user_service import get_user

router = APIRouter(prefix=f"/{APIPrefixesEnum.DRAFTS.value}")


@router.post("/create", response_model=DraftSchema, status_code=status.HTTP_201_CREATED)
async def create_draft(
    draft: CreateDraftSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = DraftRepo(db)
        service = DraftService(repo)
        draft = await service.create_draft(user.username, draft)
    return draft


@router.get(
    "/all",
    response_model=list[LittleDraftSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_drafts(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    desc_order: Annotated[bool, Query(description="DESC if True ASC otherwise.")] = True,
):
    async with UnitOfWork(db):
        repo = DraftRepo(db)
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
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
    desc_order: Annotated[bool, Query(description="DESC if True ASC otherwise.")] = True,
):
    await check_permission(
        db,
        token.role,
        username,
        user,
        RoutesEnum.GET_ALL_DRAFTS_BY_USERNAME,
        permission_setting,
    )
    async with UnitOfWork(db):
        repo = DraftRepo(db)
        service = DraftService(repo)
        drafts = await service.get_all(username, desc_order)
    return drafts


@router.get("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def get_one_draft(
    draft_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = DraftRepo(db)
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
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    await check_permission(
        db,
        token.role,
        username,
        user,
        RoutesEnum.GET_ONE_DRAFT_BY_USERNAME,
        permission_setting,
    )
    async with UnitOfWork(db):
        repo = DraftRepo(db)
        service = DraftService(repo)
        draft = await service.get_one(draft_id, username)
    return draft


@router.put("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def update_draft(
    draft_id: int,
    draft: UpdateDraftSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = DraftRepo(db)
        service = DraftService(repo)
        draft = await service.update_draft(draft_id, draft, user.username)
    return draft


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = DraftRepo(db)
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
    db: Annotated[AsyncSession, Depends(get_db)],
):
    async with UnitOfWork(db):
        repo = DraftRepo(db)
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
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
):
    async with UnitOfWork(db):
        repo = PostRepo(db)
        service = PostService(repo)
        link = await service.create_post(draft_id, post, user.username)
    return f"{str(reqeust.base_url)}@{user.username}/{link}"
