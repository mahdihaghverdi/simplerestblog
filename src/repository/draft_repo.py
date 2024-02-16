from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import insert, select, Select, desc, update

from src.core.exceptions import DraftNotFoundError, ResourceNotFoundError
from src.core.schemas import DraftSchema, LittleDraftSchema
from src.repository import BaseRepo
from src.repository.models import DraftModel, UserModel


class DraftRepo(BaseRepo):
    model = DraftModel

    async def add(self, draft: dict) -> DraftSchema:
        stmt = (
            insert(self.model)
            .values(**draft)
            .returning(
                self.model.id,
                self.model.created,
                self.model.title,
                self.model.body,
                self.model.updated,
                self.model.username,
                self.model.draft_hash,
            )
        )
        draft = await self.execute_mappings_fetchone(stmt)
        return DraftSchema(**draft)

    async def get(self, draft_id: int, username: str) -> DraftSchema:
        stmt = (
            self._select_all_columns()
            .join(UserModel)
            .where(self.model.username == username)
            .where(self.model.id == draft_id)
        )
        raw_draft = await self.execute_mappings_fetchone(stmt)
        if raw_draft is not None:
            return DraftSchema(**raw_draft)
        raise DraftNotFoundError(draft_id=draft_id)

    def _select_all_columns(self) -> Select:
        return select(
            self.model.id,
            self.model.created,
            self.model.title,
            self.model.body,
            self.model.updated,
            self.model.username,
            self.model.draft_hash,
        )

    async def get_all(self, username: str, desc_order: bool) -> list[LittleDraftSchema]:
        stmt = (
            select(
                self.model.id,
                self.model.title,
                self.model.updated,
            )
            .join(UserModel)
            .where(self.model.username == username)
            .order_by(
                desc(self.model.created) if desc_order else self.model.created,
            )
        )
        raw_drafts = await self._execute_mappings_fetchall(stmt)
        return [LittleDraftSchema(**draft, link=None) for draft in raw_drafts]

    async def update(self, draft_id: int, draft: dict, username: str) -> DraftSchema:
        stmt = (
            update(self.model)
            .values(**draft, updated=datetime.now(tz=ZoneInfo("UTC")))
            .where(self.model.username == username)
            .where(self.model.id == draft_id)
            .returning(
                self.model.id,
                self.model.created,
                self.model.title,
                self.model.body,
                self.model.updated,
                self.model.username,
            )
        )
        draft = await self.execute_mappings_fetchone(stmt)
        if draft is not None:
            return DraftSchema(**draft)
        raise DraftNotFoundError(draft_id=draft_id)

    async def _execute_mappings_fetchall(self, stmt) -> list[dict]:
        drafts = (await self.session.execute(stmt)).mappings().fetchall()
        return [dict(**draft) for draft in drafts]

    async def delete(self, draft_id: int, username: str) -> None:
        stmt = (
            select(self.model)
            .where(self.model.username == username)
            .where(self.model.id == draft_id)
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is None:
            raise DraftNotFoundError(draft_id)
        await self.session.delete(record)

    async def get_by_link(self, username: str, link: str) -> DraftSchema:
        stmt = (
            self._select_all_columns()
            .join(UserModel)
            .where(self.model.username == username)
            .where(self.model.draft_hash == link)
        )
        draft = await self.execute_mappings_fetchone(stmt)
        if draft is not None:
            return DraftSchema(**draft)
        raise ResourceNotFoundError("Draft is not Found!")
