from src.core.config import settings
from src.core.enums import APIPrefixesEnum
from src.core.schemas import PublishDraftSchema, PostSchema, LittlePostSchema
from src.repository.post_repo import PostRepo
from src.service import Service


class PostService(Service[PostRepo]):
    async def create_post(
        self,
        draft_id: int,
        post: PublishDraftSchema,
        username: str,
    ) -> str:
        data = post.model_dump()
        data["draft_id"] = draft_id
        data["username"] = username
        link = await self.repo.add(data)
        return link

    async def get_global_post(self, username: str, link: str) -> PostSchema:
        return await self.repo.get_by_link(username, link)

    async def get_all_posts(self, username: str) -> list[LittlePostSchema]:
        return await self.repo.get_all(username)

    async def unpublish_post(self, post_id: int) -> str:
        draft_id = await self.repo.unpublish(post_id)
        url = f"{settings.PREFIX}/{APIPrefixesEnum.DRAFTS.value}/{draft_id}"
        return url[1:]
