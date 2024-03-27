from typing import Literal

from sqlalchemy import insert, update, select, String, desc, func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlalchemy.sql import expression
from sqlalchemy_utils import Ltree
from sqlalchemy_utils.types.ltree import LQUERY

from src.core.exceptions import PostNotFoundError, CommentNotFoundError
from src.core.schemas import CommentReplySchema
from src.repository import BaseRepo
from src.repository.models import CommentModel, PostModel


class CommentReplyRepo(BaseRepo):
    model = CommentModel

    async def add(self, comment_data: dict) -> CommentReplySchema:
        post_id = comment_data["post_id"]
        await self._check_post_existence(post_id)

        stmt = (
            insert(self.model)
            .values(**comment_data)
            .returning(self.model.id, self.model.parent_id)
        )

        try:
            comment = await self.execute_mappings_fetchone(stmt)
        except IntegrityError:
            raise CommentNotFoundError(comment_data["parent_id"])
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
            return CommentReplySchema(**comment, reply_count=0)

    async def _check_post_existence(self, post_id):
        if (
            await self.session.execute(
                select(PostModel.id).where(PostModel.id == post_id)
            )
        ).first() is None:
            raise PostNotFoundError(post_id)

    async def get(
        self,
        post_id: int,
        page: int,
        how_many: int,
        order: Literal["first", "last", "most_replied"],
        parent_id: int | None = None,
    ) -> list[CommentReplySchema]:
        await self._check_post_existence(post_id)

        _order = None
        c = aliased(self.model, name="c")

        match order:
            case "first":
                _order = c.commented
            case "last":
                _order = desc(c.commented)
            case "most_replied":
                _order = desc(text("reply_count"))
            case _:
                _order = desc(c.commented)

        c2 = aliased(self.model, name="c2")
        sq = (
            select(func.count("*"))
            .select_from(c2)
            .filter(
                c2.path.lquery(
                    expression.cast(
                        func.concat(
                            expression.cast(c.path, String),
                            expression.cast(".*{1}", String),
                        ),
                        LQUERY,
                    )
                )
            )
            .scalar_subquery()
            .label("reply_count")
        )

        stmt = (
            select(
                c.id,
                c.commented,
                c.comment,
                expression.cast(c.path, String),
                c.updated,
                c.parent_id,
                c.username,
                sq,
            )
            .join(PostModel, PostModel.id == post_id)
            .where(c.parent_id == parent_id)
            .order_by(_order)
            .offset((page - 1) * how_many)
            .limit(how_many)
        )
        comments = await self.execute_mappings_fetchall(stmt)
        return [CommentReplySchema(**comment) for comment in comments]

    async def update(
        self, comment_data: dict, comment_id: int, post_id: int
    ) -> CommentReplySchema:
        await self._check_post_existence(post_id)

        stmt = (
            update(self.model)
            .where(self.model.id == comment_id)
            .values(**comment_data)
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
        sq = (
            select(func.count("*"))
            .select_from(self.model)
            .filter(
                self.model.path.lquery(
                    expression.cast(
                        expression.cast(f"{comment_id}" + ".*{1}", String),
                        LQUERY,
                    )
                )
            )
        )
        comment = await self.execute_mappings_fetchone(stmt)
        if comment is not None:
            reply_count = (await self.session.execute(sq)).scalar_one()
            return CommentReplySchema(**comment, reply_count=reply_count)
        raise CommentNotFoundError(comment_id)

    async def delete(self, post_id: int, comment_id: int):
        await self._check_post_existence(post_id)
        comment: CommentModel = (
            await self.session.execute(
                select(self.model).where(self.model.id == comment_id)
            )
        ).scalar_one_or_none()
        if comment is None:
            raise CommentNotFoundError(comment_id)
        await self.session.delete(comment)
