import zoneinfo
from datetime import datetime

from sqlalchemy import Integer, BigInteger, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    # profile
    name: Mapped[str | None] = mapped_column(String(32))
    bio: Mapped[str | None] = mapped_column(String(256))
    email: Mapped[str | None]
    telegram: Mapped[str | None]
    instagram: Mapped[str | None]
    twitter: Mapped[str | None]
