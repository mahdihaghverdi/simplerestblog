import hashlib
from datetime import datetime

from src.core.config import settings
from src.core.enums import APIPrefixesEnum, APIMethodsEnum
from src.core.schemas import (
    DraftSchema,
    CreateDraftSchema,
    LittleDraftSchema,
    UpdateDraftSchema,
)
from src.repository.draft_repo import DraftRepo
from src.service import Service


def draft_hash(username) -> str:
    to_hash = f"{datetime.now().isoformat()}-{username}".encode()
    return hashlib.sha256(to_hash).hexdigest()[:16]


class DraftService(Service[DraftRepo]):
    async def create_draft(self, username: str, draft: CreateDraftSchema) -> DraftSchema:
        raw_draft = draft.model_dump()
        raw_draft["username"] = username
        raw_draft["draft_hash"] = draft_hash(username)
        draft = await self.repo.add(raw_draft)
        draft.draft_hash = (
            f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/open-read/@{username}/"
            + "{}"
        ).format(draft.draft_hash)
        return draft

    async def get_one(self, draft_id: int, username: str) -> DraftSchema:
        return await self.repo.get(draft_id, username)

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
        return await self.repo.update(draft_id, draft.model_dump(), username)

    async def delete_draft(self, draft_id: int, username: str) -> None:
        await self.repo.delete(draft_id, username)

    async def get_global(self, username: str, slug: str) -> DraftSchema:
        return await self.repo.get_by_link(username, slug)
