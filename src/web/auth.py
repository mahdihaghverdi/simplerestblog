from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.schemas import Token, TokenData
from src.core.security import create_access_token
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService

router = APIRouter(prefix="/auth")


@router.post("/access-token", response_model=Token)
async def login_for_access_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        user = await service.authenticate(form_data.username, form_data.password)
        access_token = create_access_token(TokenData(username=user.username))
        return Token(access_token=access_token)
