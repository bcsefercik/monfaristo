from __future__ import annotations

import datetime
import enum
from typing import List, Optional

from models import TimeStampedBase
from settings.database import Base
from sqlalchemy import Column, Enum, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

user_has_scope = Table(
    "user_has_scope",
    Base.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("user_scope_id", ForeignKey("user_scope.id")),
)


class User(TimeStampedBase):
    __tablename__ = "user"

    class Type(enum.Enum):
        USER = "user"
        TRADER = "trader"
        ADMIN = "admin"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    first_name: Mapped[Optional[str]] = mapped_column()
    last_name: Mapped[Optional[str]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    role: Mapped[str] = mapped_column(Enum(Type), default=Type.USER, index=True)
    scopes: Mapped[List["UserScope"]] = relationship(
        secondary="user_has_scope", back_populates="users"
    )
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="owner")


class UserScope(Base):
    __tablename__ = "user_scope"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    users: Mapped[List["User"]] = relationship(
        secondary="user_has_scope", back_populates="scopes"
    )


class Account(TimeStampedBase):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    owner: Mapped["User"] = relationship(back_populates="accounts")
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
