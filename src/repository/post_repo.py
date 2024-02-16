from sqlalchemy import select

from src.core.exceptions import DraftNotFoundError
from src.core.schemas import PostSchema
from src.repository import BaseRepo
from src.repository.models import DraftModel, PostModel
from src.repository.tag_repo import TagRepo


class PostRepo(BaseRepo):
    model = PostModel

    async def add(self, data: dict) -> PostSchema:
        draft_existence_stmt = select(
            DraftModel.title,
            DraftModel.body,
            DraftModel.draft_hash,
        ).where(DraftModel.id == data["draft_id"])
        draft = (await self.session.execute(draft_existence_stmt)).mappings().fetchone()
        if draft is None:
            raise DraftNotFoundError(draft_id=data["draft_id"])

        _ts = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(_ts)

        post_model = self.model(**data)
        for tag in tags:
            post_model.tags.add(tag)

        self.session.add(post_model)
        post = PostSchema(
            title=draft["title"],
            body=draft["body"],
            draft_hash=draft["draft_hash"],
            username=data["username"],
            slug=data["slug"],
            tags={tag.tag for tag in tags},
            published=data["published"],
        )
        return post
