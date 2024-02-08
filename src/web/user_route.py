from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.schemas import UserOutSchema, UserSignupSchema

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
    return user_data
