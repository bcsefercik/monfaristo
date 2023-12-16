import datetime
from typing import Optional

from models import TimeStampedBase
from sqlalchemy.orm import Mapped, mapped_column


class User(TimeStampedBase):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    first_name: Mapped[Optional[str]] = mapped_column()
    last_name: Mapped[Optional[str]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
