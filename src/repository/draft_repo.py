from sqlalchemy import insert, select, Select

from src.core.schemas import DraftSchema
from src.repository import BaseRepo
from src.repository.models import DraftModel, UserModel


class DraftRepo(BaseRepo):
    model = DraftModel

    async def add(self, draft: dict) -> DraftSchema | None:
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

    def _select_all_columns(self) -> Select:
        return select(
            self.model.id,
            self.model.created,
            self.model.title,
            self.model.body,
            self.model.updated,
            self.model.username,
        )
