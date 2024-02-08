from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src.core.schemas import UserSignupSchema, UserSchema
from src.repository import BaseRepo
from src.repository.models import UserModel


class UserRepo(BaseRepo):
    async def add(self, user: UserSignupSchema) -> UserSchema | None:
        stmt = (
            insert(UserModel)
            .values(**user.model_dump())
            .returning(
                UserModel.username,
                UserModel.password,
                UserModel.created,
                UserModel.name,
                UserModel.bio,
                UserModel.email,
                UserModel.telegram,
                UserModel.instagram,
                UserModel.twitter,
            )
        )
        try:
            raw_user = (await self.session.execute(stmt)).mappings().fetchone()
        except IntegrityError:
            return None
        return UserSchema(**raw_user)
