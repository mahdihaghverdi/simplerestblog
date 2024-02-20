from sqlalchemy import select, func

from src.core.exceptions import (
    DraftNotFoundError,
    DraftPublishedBeforeError,
    PostNotFoundError,
)
from src.core.schemas import PostSchema
from src.repository import BaseRepo
from src.repository.models import DraftModel, PostModel, TagModel, association_table, CommentModel
from src.repository.tag_repo import TagRepo


class PostRepo(BaseRepo):
    model = PostModel

    async def add(self, data: dict) -> str:
        draft_existence_stmt = select(DraftModel).where(
            DraftModel.id == data["draft_id"]
        )
        draft: DraftModel = (
            await self.session.execute(draft_existence_stmt)
        ).scalar_one_or_none()
        if draft is None:
            raise DraftNotFoundError(draft_id=data["draft_id"])

        if draft.is_published:
            raise DraftPublishedBeforeError(draft_id=data["draft_id"])

        _ts = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(_ts)

        data["slug"] = f"{data['slug']}-{draft.draft_hash}"
        post_model = self.model(**data)
        for tag in tags:
            post_model.tags.add(tag)

        draft.is_published = True
        self.session.add_all([post_model, draft])

        return post_model.slug

    async def get_by_link(self, username: str, link: str) -> PostSchema:
        post_itself_subquery = (
            select(
                DraftModel.title,
                DraftModel.body,
                DraftModel.updated,
                self.model.published,
                self.model.id,
            )
            .join(self.model.draft)
            .join(self.model.user)
            .where(self.model.username == username)
            .where(self.model.slug == link)
        ).subquery("post_itself")

        post_with_tags = (
            select(post_itself_subquery, func.array_agg(TagModel.tag).label("tags"))
            .outerjoin(
                association_table.join(TagModel),
                post_itself_subquery.columns.id  # noqa
                == association_table.columns.post_id,
            )
            .group_by(post_itself_subquery)
        ).subquery('post_with_tags')

        comments_count = (
            (
                select(func.count("*"))
                .select_from(CommentModel)
                .where(CommentModel.post_id == post_with_tags.columns.id)
                .where(CommentModel.parent_id == None)  # noqa: E711
            )
            .scalar_subquery()
            .label("comments_count")
        )

        post_tags_comments_count = select(post_with_tags, comments_count)
        raw_post = await self.execute_mappings_fetchone(post_tags_comments_count)
        if raw_post is None:
            raise PostNotFoundError(link)
        return PostSchema(**raw_post)
