import datetime
import enum
from typing import List, Optional

from models import TimeStampedBase
from settings.database import Base
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


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
    __tablename__ = "user_permission"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    users: Mapped[List["User"]] = relationship(
        secondary="user_has_scope", back_populates="scopes"
    )


class UserHasScope(TimeStampedBase):
    __tablename__ = "user_has_scope"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), index=True, primary_key=True
    )
    user: Mapped[User] = relationship()
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("user_permission.id"), index=True, primary_key=True
    )
    permission: Mapped[UserScope] = relationship()
    is_active: Mapped[bool] = mapped_column(default=True, index=True)


class Account(TimeStampedBase):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    owner: Mapped["User"] = relationship(back_populates="accounts")
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
