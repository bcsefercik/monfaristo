import datetime
import enum
from typing import List, Optional

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
    cumulative_ticker_holding_id: Mapped[int] = mapped_column(
        ForeignKey("cumulative_ticker_holding.id"), index=True
    )
    cumulative_ticker_holding: Mapped["CumulativeTickerHolding"] = relationship(
        back_populates="transactions"
    )


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
    count: Mapped[float] = mapped_column(default=0)
    total_buys: Mapped[int] = mapped_column(default=0)
    total_sells: Mapped[int] = mapped_column(default=0)
    total_commission_cost: Mapped[float] = mapped_column(default=0)
    total_buy_amount: Mapped[float] = mapped_column(default=0)
    total_sell_amount: Mapped[float] = mapped_column(default=0)
    is_completed: Mapped[bool] = mapped_column(default=False, index=True)
    first_transction_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    last_transaction_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        default=None, nullable=True
    )
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="cumulative_ticker_holding"
    )

    @property
    def adjusted_avg_cost(self) -> float | None:
        return (
            (
                (
                    self.total_buy_amount
                    + self.total_commission_cost
                    - self.total_sell_amount
                )
                / self.count
            )
            if self.count > 0 and not self.is_completed
            else None
        )

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

            # update liquid asset account balance
            liquid_asset_account.balance -= transaction.price * transaction.count
            liquid_asset_account.balance -= transaction.commission

            # do following updates at the end
            self.count += transaction.count
            self.total_buys += transaction.count
            self.total_buy_amount += transaction.price * transaction.count

            self.first_transction_at = min(
                self.first_transction_at, transaction.executed_at
            )

        elif transaction.type == Transaction.Type.SELL:
            if transaction.count > self.count:
                return False

            # update liquid asset account balance
            liquid_asset_account.balance += transaction.price * transaction.count
            liquid_asset_account.balance -= transaction.commission

            # do following updates at the end
            self.count -= transaction.count
            self.total_sells += transaction.count
            self.total_sell_amount += transaction.price * transaction.count

        self.total_commission_cost += transaction.commission

        if self.count == 0:
            self.is_completed = True

            if self.last_transaction_at is None:
                self.last_transaction_at = transaction.executed_at
            else:
                self.last_transaction_at = max(
                    self.last_transaction_at, transaction.executed_at
                )

        session.flush()

        return True
