from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.acl import get_permission_setting, ACLSetting
from src.core.database import get_db
from src.core.schemas import (
    LittleDraftSchema,
    UserSchema,
    TokenData,
    DraftSchema,
    CreateDraftSchema,
    UpdateDraftSchema,
)
from src.core.security import validate_token
from src.service.user_service import get_user

router = APIRouter(prefix="drafts", tags=["drafts"])


@router.post("/", response_model=DraftSchema, status_code=status.HTTP_201_CREATED)
async def create_draft(
    draft: CreateDraftSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.get("/", response_model=list[LittleDraftSchema], status_code=status.HTTP_200_OK)
async def get_all_drafts(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.get("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def get_one_draft(
    draft_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.put("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def update_draft(
    draft_id: int,
    draft: UpdateDraftSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.get("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


# publish route will be written after considerations