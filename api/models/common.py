import datetime
import enum
import platform
from typing import Optional

from models import Base
from models.user import InvestmentAccount, User
from settings.database import TimeStampedBase
from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint, desc
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship


class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    symbol: Mapped[Optional[str]] = mapped_column(String(32), index=True)


class Platform(Base):
    __tablename__ = "platform"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    url: Mapped[Optional[str]] = mapped_column()
    logo_url: Mapped[Optional[str]] = mapped_column()


class Market(Base):
    __tablename__ = "market"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str] = mapped_column(String(255), index=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"))
    currency: Mapped["Currency"] = relationship()
    description: Mapped[Optional[str]] = mapped_column()

    __table_args__ = (
        UniqueConstraint("code", "currency_id", name="_market__code_currency_uc"),
    )


class Ticker(Base):
    __tablename__ = "ticker"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("market.id"))
    market: Mapped["Market"] = relationship()
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    url: Mapped[Optional[str]] = mapped_column()
    logo_url: Mapped[Optional[str]] = mapped_column()

    __table_args__ = (
        UniqueConstraint("code", "market_id", name="_ticker__code_market_uc"),
    )


class LiquidAssetAccount(TimeStampedBase):
    __tablename__ = "liquid_asset_account"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(
        String, index=True, default=None, nullable=True
    )  # None means "default" account for the platform
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id"), index=True)
    platform: Mapped[Platform] = relationship()
    balance: Mapped[float] = mapped_column(default=0)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), index=True)
    currency: Mapped["Currency"] = relationship()
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    owner: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "title",
            "currency_id",
            "owner_id",
            "platform_id",
            name="_liquid_asset__title_currency_owner_platform_uc",
        ),
    )

    def add_transaction(
        self, session: Session, transaction: "LiquidAssetTransaction"
    ) -> bool:
        if not (
            self.currency_id == transaction.liquid_asset_account.currency_id
            and self.owner_id == transaction.liquid_asset_account.owner_id
            and self.platform_id == transaction.liquid_asset_account.platform_id
        ):
            return False

        if transaction.type in (
            LiquidAssetTransaction.Type.DEPOSIT,
            LiquidAssetTransaction.Type.DIVIDEND,
        ):
            self.balance += transaction.amount
        elif transaction.type == LiquidAssetTransaction.Type.WITHDRAW:
            self.balance -= transaction.amount
        else:
            raise ValueError(f"Invalid transaction type: {transaction.type}")

        session.flush()

        return True


class LiquidAssetTransaction(Base):
    __tablename__ = "liquid_asset_transaction"

    class Type(str, enum.Enum):
        DEPOSIT = "DEPOSIT"
        WITHDRAW = "WITHDRAW"
        DIVIDEND = "DIVIDEND"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    liquid_asset_account_id: Mapped[int] = mapped_column(
        ForeignKey("liquid_asset_account.id"), index=True
    )
    liquid_asset_account: Mapped[LiquidAssetAccount] = relationship()
    executed_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )
    amount: Mapped[float] = mapped_column()
    type: Mapped[Type] = mapped_column(Enum(Type), index=True)
    description: Mapped[Optional[str]] = mapped_column(
        String, default=None, nullable=True
    )
