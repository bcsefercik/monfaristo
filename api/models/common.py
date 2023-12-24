import enum
from typing import Optional

from models import Base
from models.user import Account, User
from settings.database import TimeStampedBase
from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


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


class LiquidAsset(TimeStampedBase):
    __tablename__ = "liquid_asset"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(
        String, index=True, default=None, nullable=True
    )
    amount: Mapped[float] = mapped_column(default=0)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), index=True)
    currency: Mapped["Currency"] = relationship()
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    owner: Mapped["User"] = relationship()
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id"), index=True, nullable=True, default=None
    )  # account_id can be null for non-account assets
    account: Mapped["Account"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "title",
            "currency_id",
            "owner_id",
            "account_id",
            name="_liquid_asset__title_currency_owner_account_uc",
        ),
    )
