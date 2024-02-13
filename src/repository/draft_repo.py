from sqlalchemy import insert

from src.core.schemas import DraftSchema
from src.repository import BaseRepo
from src.repository.models import DraftModel


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
