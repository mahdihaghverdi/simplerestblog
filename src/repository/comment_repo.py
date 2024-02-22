from sqlalchemy import insert, update, select, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression
from sqlalchemy_utils import Ltree

from src.core.exceptions import PostNotFoundError
from src.core.schemas import CommentReplySchema
from src.repository import BaseRepo
from src.repository.models import CommentModel


class CommentReplyRepo(BaseRepo):
    model = CommentModel

    async def add(self, comment_data: dict) -> CommentReplySchema:
        stmt = (
            insert(self.model)
            .values(**comment_data)
            .returning(self.model.id, self.model.parent_id)
        )

        try:
            comment = await self.execute_mappings_fetchone(stmt)
        except IntegrityError:
            raise PostNotFoundError(comment_data["post_id"])
        else:
            cmt_id = comment["id"]

            add_path_stmt = (
                update(self.model)
                .where(self.model.id == cmt_id)
                .returning(
                    self.model.id,
                    self.model.commented,
                    self.model.comment,
                    expression.cast(self.model.path, String),
                    self.model.updated,
                    self.model.parent_id,
                    self.model.username,
                )
            )
            if comment["parent_id"] is None:
                # it s a comment
                add_path_stmt = add_path_stmt.values(path=Ltree(str(cmt_id)))
            else:
                # it is reply
                # new_path = parent_path.self_path
                parent_path = (
                    await self.session.execute(
                        select(self.model.path).where(
                            self.model.id == comment["parent_id"]
                        )
                    )
                ).scalar_one()
                add_path_stmt = add_path_stmt.values(
                    path=Ltree(parent_path) + Ltree(str(cmt_id))
                )

            comment = await self.execute_mappings_fetchone(add_path_stmt)
            return CommentReplySchema(**comment)
