import zoneinfo
from datetime import datetime

from sqlalchemy import Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow():
    return datetime.now(tz=zoneinfo.ZoneInfo("UTC"))


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserModel(Base):
    __tablename__ = "users"

    # credentials
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str]
    role: Mapped[str]

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

    def __repr__(self):
        return f"<User: {self.username!r}>"


class DraftModel(Base):
    __tablename__ = "drafts"

    title: Mapped[str]
    body: Mapped[str]
    updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tmplink: Mapped[str]

    # relation
    username: Mapped[str] = mapped_column(ForeignKey("users.username"))
    user: Mapped["UserModel"] = relationship(back_populates="drafts")

    def __repr__(self):
        return f"<Draft: {self.title!r}>"
