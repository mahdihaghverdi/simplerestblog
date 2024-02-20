from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import PostNotFoundError
from src.core.schemas import CommentSchema
from src.repository import BaseRepo
from src.repository.models import CommentModel


class CommentRepo(BaseRepo):
    model = CommentModel

    async def add(self, comment_data: dict) -> CommentSchema:
        stmt = (
            insert(self.model)
            .values(**comment_data)
            .returning(
                self.model.id,
                self.model.commented,
                self.model.comment,
                self.model.path,
                self.model.updated,
                self.model.parent_id,
                self.model.username,
            )
        )

        try:
            comment = await self.execute_mappings_fetchone(stmt)
        except IntegrityError:
            raise PostNotFoundError(comment_data["post_id"])
        else:
            return CommentSchema(**comment)
