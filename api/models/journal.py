import datetime
import enum
from typing import Optional

import ipdb
from models import Base, TimeStampedBase
from models.common import LiquidAsset, Platform, Ticker
from models.user import Account, User
from requests import Session
from settings.database import SessionLocal, get_db, get_or_create
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


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
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), index=True)
    account: Mapped[Account] = relationship()
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id"), index=True)
    platform: Mapped[Platform] = relationship()
    executed_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
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


class CumulativeTickerHolding(TimeStampedBase):
    # TODO: Write tests for this model

    __tablename__ = "cumulative_ticker_holding"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker.id"), index=True)
    ticker: Mapped[Ticker] = relationship()
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), index=True)
    account: Mapped["Account"] = relationship()
    avg_cost: Mapped[float] = mapped_column(default=0)
    adjusted_avg_cost: Mapped[float] = mapped_column(default=0)
    count: Mapped[float] = mapped_column(default=0)
    total_buys: Mapped[int] = mapped_column(default=0)
    total_sells: Mapped[int] = mapped_column(default=0)
    realized_pnl: Mapped[float] = mapped_column(default=0)
    is_completed: Mapped[bool] = mapped_column(default=False, index=True)

    def add_transaction(self, session: Session, transaction: Transaction) -> bool:
        if not (
            self.ticker_id == transaction.ticker_id
            and self.account_id == transaction.account_id
        ):
            return False

        liquid_asset, created = get_or_create(
            session,
            LiquidAsset,
            currency_id=self.ticker.market.currency_id,
            owner_id=self.account.owner_id,
            account_id=self.account_id,
        )
        session.flush()

        if transaction.type == Transaction.Type.BUY:
            self.avg_cost = (
                self.total_buys * self.avg_cost + transaction.price * transaction.count
            ) / (self.total_buys + transaction.count)
            self.adjusted_avg_cost = (
                self.count * self.adjusted_avg_cost
                + transaction.price * transaction.count
            ) / (self.count + transaction.count)

            # update asset
            liquid_asset.amount -= transaction.price * transaction.count
            liquid_asset.amount -= transaction.commission

            # do following updates at the end
            self.count += transaction.count
            self.total_buys += transaction.count

        elif transaction.type == Transaction.Type.SELL:
            if transaction.count > self.count:
                return False

            self.adjusted_avg_cost = (
                self.count * self.adjusted_avg_cost
                - transaction.price * transaction.count
            ) / (self.count - transaction.count)

            self.realized_pnl += (transaction.price - self.avg_cost) * transaction.count

            # update asset
            liquid_asset.amount += transaction.price * transaction.count
            liquid_asset.amount -= transaction.commission

            # do following updates at the end
            self.count -= transaction.count
            self.total_sells += transaction.count

        if self.count == 0:
            self.is_completed = True

        session.flush()

        return True
