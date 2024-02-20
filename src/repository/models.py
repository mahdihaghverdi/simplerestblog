import zoneinfo
from datetime import datetime

from sqlalchemy import Integer, BigInteger, String, DateTime, ForeignKey, Table, Column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_utils import LtreeType


def utcnow():
    return datetime.now(tz=zoneinfo.ZoneInfo("UTC"))


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )


class UserModel(Base):
    __tablename__ = "users"

    # credentials
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str]
    role: Mapped[str]
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # profile
    name: Mapped[str | None] = mapped_column(String(32))
    bio: Mapped[str | None] = mapped_column(String(256))
    email: Mapped[str | None]
    telegram: Mapped[str | None]
    instagram: Mapped[str | None]
    twitter: Mapped[str | None]

    # relations
    drafts: Mapped[list["DraftModel"]] = relationship(
        back_populates="user",
        cascade="delete, delete-orphan",
    )
    posts: Mapped[list["PostModel"]] = relationship(
        back_populates="user",
        cascade="delete, delete-orphan",
    )
    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="user",
        cascade="delete, delete-orphan",
    )

    def __repr__(self):
        return f"<User: {self.username!r}>"


class DraftModel(Base):
    __tablename__ = "drafts"

    title: Mapped[str]
    body: Mapped[str]
    updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    draft_hash: Mapped[str]
    is_published: Mapped[bool] = mapped_column(default=lambda: False)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # FK
    username: Mapped[str] = mapped_column(
        ForeignKey(f"{UserModel.__tablename__}.username"),
    )

    # relations
    user: Mapped["UserModel"] = relationship(back_populates="drafts")
    post: Mapped["PostModel"] = relationship(
        back_populates="draft",
        cascade="delete, delete-orphan",
    )

    def __repr__(self):
        return f"<Draft: {self.title!r}>"


class PostModel(Base):
    __tablename__ = "posts"

    slug: Mapped[str]
    published: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # FK
    draft_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DraftModel.__tablename__}.id"),
        unique=True,
    )
    username: Mapped[str] = mapped_column(
        ForeignKey(f"{UserModel.__tablename__}.username"),
    )

    # relations
    draft: Mapped["DraftModel"] = relationship(back_populates="post")
    user: Mapped["UserModel"] = relationship(back_populates="posts")
    tags: Mapped[set["TagModel"]] = relationship(secondary="association_table")
    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="post",
        cascade="delete, delete-orphan",
    )

    def __repr__(self):
        return f"<Post:{self.slug!r}>"


class TagModel(Base):
    __tablename__ = "tags"

    tag: Mapped[str] = mapped_column(unique=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    def __repr__(self):
        return f"<TagModel: tag={self.tag!r}>"


association_table = Table(
    "association_table",
    Base.metadata,
    Column("post_id", ForeignKey(f"{PostModel.__tablename__}.id"), primary_key=True),
    Column("tag_id", ForeignKey(f"{TagModel.__tablename__}.id"), primary_key=True),
)


class CommentModel(Base):
    __tablename__ = "comments"

    comment: Mapped[str] = mapped_column(String(256))
    path: Mapped[str | None] = mapped_column(LtreeType)
    commented: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # FK
    post_id: Mapped[int] = mapped_column(
        ForeignKey(f"{PostModel.__tablename__}.id"),
    )
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    username: Mapped[str] = mapped_column(
        ForeignKey(f"{UserModel.__tablename__}.username"),
    )

    # relations
    user: Mapped["UserModel"] = relationship(back_populates="comments")
    post: Mapped["PostModel"] = relationship(back_populates="comments")
    children: Mapped[list["CommentModel"]] = relationship(
        cascade="delete, delete-orphan",
    )
