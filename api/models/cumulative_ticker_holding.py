import datetime
import enum
from functools import cached_property
from typing import Callable, List, Optional

import ipdb
from models import Base, TimeStampedBase
from models.common import LiquidAssetAccount, Platform, Ticker
from models.journal import Transaction
from models.user import InvestmentAccount, User
from pydantic import BaseModel
from settings.database import SessionLocal, get_db, get_or_create
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship


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
    first_transaction_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow()
    )
    last_transaction_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        default=None, nullable=True
    )
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="cumulative_ticker_holding"
    )

    @cached_property
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

    @hybrid_property
    def pnl_amount(self) -> float | None:
        return (
            (
                self.total_sell_amount
                - self.total_buy_amount
                - self.total_commission_cost
            )
            if self.is_completed
            else None
        )

    @hybrid_property
    def pnl_ratio(self) -> float | None:
        return (
            (self.pnl_amount / (self.total_buy_amount + self.total_commission_cost))
            if self.pnl_amount is not None
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

            self.first_transaction_at = min(
                self.first_transaction_at, transaction.executed_at
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


class CumulativeTickerHoldingFilter(BaseModel):
    ticker_id: int | None = None
    investment_account_id: int | None = None
    is_completed: bool | None = None


class CumulativeTickerHoldingOrderingOptions(BaseModel):
    id: Callable | None = None
    ticker_code: Callable | None = None
    total_buy_amount: Callable | None = None
    total_sell_amount: Callable | None = None
    pnl_amount: Callable | None = None
    pnl_ratio: Callable | None = None


class CumulativeTickerHoldingRepository:
    def __init__(self, session: Session):
        self._session = session
        self._simple_ordering_options = (
            "id",
            "total_buy_amount",
            "total_sell_amount",
            "pnl_amount",
            "pnl_ratio",
        )

    def get_all(
        self,
        filter: CumulativeTickerHoldingFilter,
        ordering: CumulativeTickerHoldingOrderingOptions,
    ) -> List[CumulativeTickerHolding]:
        query = self._session.query(CumulativeTickerHolding)

        if filter.investment_account_id is not None:
            query = query.filter(
                CumulativeTickerHolding.investment_account_id
                == filter.investment_account_id
            )

        if filter.ticker_id is not None:
            query = query.filter(CumulativeTickerHolding.ticker_id == filter.ticker_id)

        if filter.is_completed is not None:
            query = query.filter(
                CumulativeTickerHolding.is_completed == filter.is_completed
            )

        for opk, opv in ordering.model_dump().items():
            if opv is None:
                continue

            if opk not in self._simple_ordering_options:
                continue

            query = query.order_by(opv(getattr(CumulativeTickerHolding, opk)))

        if ordering.ticker_code is not None:
            query = query.join(CumulativeTickerHolding.ticker).order_by(
                ordering.ticker_code(Ticker.code)
            )

        return query.all()
