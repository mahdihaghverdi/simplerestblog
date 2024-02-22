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
