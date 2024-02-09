from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.schemas import UserOutSchema, UserSignupSchema, UserSchema
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService, get_user

router = APIRouter(prefix="/users")


@router.post(
    "/signup",
    response_model=UserOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_data: UserSignupSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        user = await service.signup_user(user_data)
    return user


@router.get("/me", response_model=UserOutSchema, status_code=status.HTTP_200_OK)
async def me(user: Annotated[UserSchema, Depends(get_user)]):
    return user
