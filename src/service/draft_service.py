from src.core.schemas import DraftSchema, CreateDraftSchema
from src.repository.draft_repo import DraftRepo
from src.service import Service


class DraftService(Service[DraftRepo]):
    async def create_draft(self, username: str, draft: CreateDraftSchema) -> DraftSchema:
        raw_draft = draft.model_dump()
        raw_draft["username"] = username
        draft = await self.repo.add(raw_draft)
        return draft
