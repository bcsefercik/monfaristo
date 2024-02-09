import datetime
import enum
from functools import cached_property
from typing import Callable, List, Optional

import ipdb
from models import Base, TimeStampedBase
from models.common import LiquidAssetAccount, Market, Platform, Ticker
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
    ticker_code: str | None = None
    market_id: int | None = None
    market_code: str | None = None
    investment_account_id: int | None = None
    is_completed: bool | None = None


class CumulativeTickerHoldingOrderingOptions(BaseModel):
    ticker_code: Callable | None = None
    id: Callable | None = None
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
        self._simple_filters = (
            "ticker_id",
            "market_id",
            "investment_account_id",
            "is_completed",
        )

    def get_all(
        self,
        filter: CumulativeTickerHoldingFilter,
        ordering: CumulativeTickerHoldingOrderingOptions,
    ) -> List[CumulativeTickerHolding]:
        query = self._session.query(CumulativeTickerHolding)

        for fpk, fpv in filter.model_dump().items():
            if fpv is not None and fpk in self._simple_filters:
                query = query.filter(getattr(CumulativeTickerHolding, fpk) == fpv)

        if filter.ticker_code is not None:
            query = query.join(CumulativeTickerHolding.ticker).filter(
                Ticker.code == filter.ticker_code.upper()
            )

        if filter.market_code is not None:
            market = (
                self._session.query(Market)
                .filter(Market.code == filter.market_code.upper())
                .first()
            )

            if market is not None:
                query = query.join(CumulativeTickerHolding.ticker).filter(
                    Ticker.market_id == market.id
                )

        orders = []

        if ordering.ticker_code is not None:
            orders.append(ordering.ticker_code(Ticker.code))
            query = query.join(CumulativeTickerHolding.ticker)

        orders.extend(
            [
                opv(getattr(CumulativeTickerHolding, opk))
                for opk, opv in ordering.model_dump().items()
                if opv is not None and opk in self._simple_ordering_options
            ]
        )

        if orders:
            query = query.order_by(*orders)

        return query.all()
