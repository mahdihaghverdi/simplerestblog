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


@router.get("/", response_model=list[LittleDraftSchema], status_code=status.HTTP_200_OK)
async def get_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.get("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def get_one(
    draft_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.post("/", response_model=DraftSchema, status_code=status.HTTP_201_CREATED)
async def create(
    draft: CreateDraftSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.put("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def update(
    draft_id: int,
    draft: UpdateDraftSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


@router.get("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    draft_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserSchema, Depends(get_user)],
    token: Annotated[TokenData, Depends(validate_token)],
    permission_setting: Annotated[ACLSetting, Depends(get_permission_setting)],
):
    pass


# publish route will be written after considerations
