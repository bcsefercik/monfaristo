import datetime
import enum
from typing import Optional

import ipdb
from models import Base, TimeStampedBase
from models.common import LiquidAssetAccount, Platform, Ticker
from models.user import InvestmentAccount, User
from settings.database import SessionLocal, get_db, get_or_create
from sqlalchemy import Enum, ForeignKey, String
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
    investment_account_id: Mapped[int] = mapped_column(
        ForeignKey("investment_account.id"), index=True
    )
    investment_account: Mapped["InvestmentAccount"] = relationship()
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
            and self.investment_account_id == transaction.investment_account_id
        ):
            return False

        liquid_asset_account, created = get_or_create(
            session,
            LiquidAssetAccount,
            title=None,
            currency_id=self.ticker.market.currency_id,
            owner_id=self.investment_account.owner_id,
            platform_id=transaction.platform_id,
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

            # update liquid asset account balance
            liquid_asset_account.balance -= transaction.price * transaction.count
            liquid_asset_account.balance -= transaction.commission

            # do following updates at the end
            self.count += transaction.count
            self.total_buys += transaction.count

        elif transaction.type == Transaction.Type.SELL:
            if transaction.count > self.count:
                return False

            self.adjusted_avg_cost = (
                self.count * self.adjusted_avg_cost
                - transaction.price * transaction.count
            ) / max(1, (self.count - transaction.count))

            self.realized_pnl += (transaction.price - self.avg_cost) * transaction.count

            # update liquid asset account balance
            liquid_asset_account.balance += transaction.price * transaction.count
            liquid_asset_account.balance -= transaction.commission

            # do following updates at the end
            self.count -= transaction.count
            self.total_sells += transaction.count

        if self.count == 0:
            self.is_completed = True

        session.flush()

        return True
