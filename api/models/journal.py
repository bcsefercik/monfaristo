import datetime
import enum

from models import Base, TimeStampedBase
from models.common import Ticker
from models.user import User
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Account(TimeStampedBase):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    owner: Mapped[User] = relationship()


class Transaction(Base):
    __tablename__ = "transaction"

    class Type(enum.Enum):
        BUY = "buy"
        SELL = "sell"

    class TimeFrame(enum.Enum):
        MIN_1 = "1M"
        MIN_5 = "5M"
        MIN_15 = "15M"
        MIN_30 = "30M"
        HOUR_1 = "1H"
        HOUR_4 = "4H"
        HOUR_6 = "6H"
        HOUR_12 = "12H"
        DAILY = "DAILY"
        WEEKLY = "WEEKLY"
        MONTHLY = "MONTHLY"
        QUARTERLY = "QUARTERLY"
        YEARLY = "YEARLY"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker.id"), index=True)
    ticker: Mapped[Ticker] = relationship()
    price: Mapped[float] = mapped_column()
    commission: Mapped[float] = mapped_column()
    count: Mapped[float] = mapped_column()
    type: Mapped[Type] = mapped_column(Enum(Type), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), index=True)
    account: Mapped[Account] = relationship()
    executed_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    executed_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    executed_by: Mapped[User] = relationship()
    description: Mapped[str] = mapped_column(String, default="")
    notes: Mapped[str] = mapped_column(String, default="")
    time_frame: Mapped[TimeFrame] = mapped_column(Enum(TimeFrame), index=True)
    pattern: Mapped[str] = mapped_column(String, default=None, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
