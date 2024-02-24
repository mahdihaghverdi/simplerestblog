from typing import Literal

from src.core.schemas import CreateCommentReplySchema, CommentReplySchema
from src.repository.comment_repo import CommentReplyRepo
from src.service import Service


class CommentReplyService(Service[CommentReplyRepo]):
    async def create_comment(
        self, post_id: int, comment: CreateCommentReplySchema, username: str
    ) -> CommentReplySchema:
        data = comment.model_dump()
        data["post_id"] = post_id
        data["username"] = username
        data["parent_id"] = None
        return await self.repo.add(data)

    async def create_reply(
        self,
        post_id: int,
        comment_id: int,
        reply: CreateCommentReplySchema,
        username: str,
    ) -> CommentReplySchema:
        data = reply.model_dump()
        data["post_id"] = post_id
        data["username"] = username
        data["parent_id"] = comment_id
        return await self.repo.add(data)

    async def get_comments(
        self,
        post_id: int,
        page: int,
        how_many: int,
        order: Literal["first", "last", "most_replied"],
    ) -> list[CommentReplySchema]:
        return await self.repo.get(post_id, page, how_many, order)
