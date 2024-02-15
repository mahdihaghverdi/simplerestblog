from src.core.config import settings
from src.core.enums import APIPrefixesEnum, APIMethodsEnum
from src.core.exceptions import DraftNotFoundError
from src.core.schemas import (
    DraftSchema,
    CreateDraftSchema,
    LittleDraftSchema,
    UpdateDraftSchema,
)
from src.repository.draft_repo import DraftRepo
from src.service import Service


class DraftService(Service[DraftRepo]):
    async def create_draft(self, username: str, draft: CreateDraftSchema) -> DraftSchema:
        raw_draft = draft.model_dump()
        raw_draft["username"] = username
        draft = await self.repo.add(raw_draft)
        return draft

    async def get_one(self, draft_id: int, username: str) -> DraftSchema:
        draft = await self.repo.get(draft_id, username)
        if draft is None:
            raise DraftNotFoundError(draft_id)
        return draft

    async def get_all(self, username: str, desc_order: bool) -> list[LittleDraftSchema]:
        drafts = await self.repo.get_all(username, desc_order)
        get_url = f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/" + "{}"
        for draft in drafts:
            draft.link = (APIMethodsEnum.GET, get_url.format(draft.id))
        return drafts

    async def update_draft(
        self,
        draft_id: int,
        draft: UpdateDraftSchema,
        username: str,
    ) -> DraftSchema:
        draft = await self.repo.update(draft_id, draft.model_dump(), username)
        if draft is not None:
            return draft
        raise DraftNotFoundError(draft_id)

    async def delete_draft(self, draft_id: int, username: str) -> None:
        if not (await self.repo.delete(draft_id, username)):
            raise DraftNotFoundError(draft_id)
