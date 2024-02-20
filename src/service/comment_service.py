from src.core.schemas import CreateCommentSchema, CommentSchema
from src.repository.comment_repo import CommentRepo
from src.service import Service


class CommentService(Service[CommentRepo]):
    async def create_comment(
        self, post_id: int, comment: CreateCommentSchema, username: str
    ) -> CommentSchema:
        data = comment.model_dump()
        data["post_id"] = post_id
        data["username"] = username
        data["path"] = None
        return await self.repo.add(data)
