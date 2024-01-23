import datetime
import enum
from functools import cached_property
from typing import List, Optional

import ipdb
from models import Base, TimeStampedBase
from models.common import LiquidAssetAccount, Platform, Ticker
from models.user import InvestmentAccount, User
from settings.database import SessionLocal, get_db, get_or_create
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship


class Transaction(Base):
    __tablename__ = "transaction"

    class Type(str, enum.Enum):
        BUY = "BUY"
        SELL = "SELL"

    class TimeFrame(str, enum.Enum):
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
    count: Mapped[float] = mapped_column()
    commission: Mapped[float] = mapped_column()
    type: Mapped[Type] = mapped_column(Enum(Type), index=True)
    investment_account_id: Mapped[int] = mapped_column(
        ForeignKey("investment_account.id"), index=True
    )
    investment_account: Mapped[InvestmentAccount] = relationship()
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id"), index=True)
    platform: Mapped[Platform] = relationship()
    executed_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow()
    )
    executed_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    executed_by: Mapped[User] = relationship()
    description: Mapped[str] = mapped_column(String, default="")
    notes: Mapped[str] = mapped_column(String, default="")
    time_frame: Mapped[Optional[TimeFrame]] = mapped_column(
        Enum(TimeFrame), index=True, default=None, nullable=True
    )
    pattern: Mapped[Optional[str]] = mapped_column(String, default=None, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    cumulative_ticker_holding_id: Mapped[int] = mapped_column(
        ForeignKey("cumulative_ticker_holding.id"), index=True
    )
    cumulative_ticker_holding: Mapped["CumulativeTickerHolding"] = relationship(
        back_populates="transactions"
    )
