from sqlalchemy import insert, select, Select
from sqlalchemy.exc import IntegrityError

from src.core.enums import UserRolesEnum
from src.core.schemas import UserSchema
from src.core.security import verify_password
from src.repository import BaseRepo
from src.repository.models import UserModel


class UserRepo(BaseRepo):
    model = UserModel

    async def add(self, user: dict) -> UserSchema | None:
        stmt = (
            insert(self.model)
            .values(**user)
            .returning(
                self.model.username,
                self.model.password,
                self.model.role,
                self.model.created,
                self.model.name,
                self.model.bio,
                self.model.email,
                self.model.telegram,
                self.model.instagram,
                self.model.twitter,
            )
        )
        try:
            raw_user = await self._mappings_fetchone(stmt)
        except IntegrityError:
            return None
        return UserSchema(**raw_user)

    async def auth(self, username, password) -> UserSchema | None:
        stmt = self._select_all_columns().where(
            self.model.username == username,
        )
        raw_user = await self._mappings_fetchone(stmt)
        if raw_user is None:
            return
        if verify_password(password, raw_user["password"]):
            return UserSchema(**raw_user)

    async def get(self, username) -> UserSchema | None:
        stmt = self._select_all_columns().where(
            self.model.username == username,
        )
        raw_user = await self._mappings_fetchone(stmt)
        if raw_user is not None:
            return UserSchema(**raw_user)

    async def _mappings_fetchone(self, stmt) -> dict | None:
        raw_user = (await self.session.execute(stmt)).mappings().fetchone()
        if raw_user is not None:
            raw_user = dict(**raw_user)
            match raw_user["role"]:
                case UserRolesEnum.USER.value:
                    raw_user["role"] = UserRolesEnum.USER
                case UserRolesEnum.ADMIN.value:
                    raw_user["role"] = UserRolesEnum.ADMIN
            return dict(**raw_user)

    def _select_all_columns(self) -> Select:
        return select(
            self.model.username,
            self.model.password,
            self.model.role,
            self.model.created,
            self.model.name,
            self.model.bio,
            self.model.email,
            self.model.telegram,
            self.model.instagram,
            self.model.twitter,
        )
