from sqlalchemy import insert, select, Select
from sqlalchemy.exc import IntegrityError

from src.core.enums import UserRolesEnum
from src.core.exceptions import (
    UserNotFoundError,
    CredentialsError,
    DatabaseIntegrityError,
)
from src.core.schemas import UserSchema
from src.core.security import verify_password
from src.repository import BaseRepo
from src.repository.models import UserModel


class UserRepo(BaseRepo):
    model = UserModel

    async def add(self, user: dict) -> UserSchema:
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
                self.model.totp_hash,
            )
        )
        try:
            raw_user = await self.execute_mappings_fetchone(stmt)
        except IntegrityError as e:
            raise DatabaseIntegrityError(e)
        else:
            return UserSchema(**raw_user)

    async def auth(self, username, password) -> UserSchema:
        stmt = self._select_all_columns().where(
            self.model.username == username,
        )
        raw_user = await self.execute_mappings_fetchone(stmt)
        if raw_user is None:
            raise UserNotFoundError(username=username)
        if verify_password(password, raw_user["password"]):
            return UserSchema(**raw_user)
        raise CredentialsError()

    async def get(self, username) -> UserSchema:
        stmt = self._select_all_columns().where(
            self.model.username == username,
        )
        raw_user = await self.execute_mappings_fetchone(stmt)
        if raw_user is not None:
            return UserSchema(**raw_user)
        raise UserNotFoundError(username)

    async def username_exists(self, username) -> bool:
        try:
            await self.get(username)
        except UserNotFoundError:
            return False
        else:
            return True

    async def execute_mappings_fetchone(self, stmt) -> dict | None:
        raw_user = await super().execute_mappings_fetchone(stmt)
        if raw_user is not None:
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
