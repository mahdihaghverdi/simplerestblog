from datetime import datetime
from zoneinfo import ZoneInfo

from src.core.schemas import PublishDraftSchema, PostSchema
from src.repository.post_repo import PostRepo
from src.service import Service


class PostService(Service[PostRepo]):
    async def create_post(
        self,
        draft_id: int,
        post: PublishDraftSchema,
        username: str,
    ) -> PostSchema:
        data = post.model_dump()
        data["draft_id"] = draft_id
        data["published"] = datetime.now(tz=ZoneInfo("UTC"))
        data["username"] = username
        post = await self.repo.add(data)
        return post
