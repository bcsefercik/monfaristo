from typing import Optional

from models import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str] = mapped_column(String(255), index=True)
    symbol: Mapped[Optional[str]] = mapped_column(String(32), index=True)


class Platform(Base):
    __tablename__ = "platform"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
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


class Asset(Base):
    __tablename__ = "asset"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    ticker: Mapped[str] = mapped_column(String(50), index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("market.id"))
    market: Mapped["Market"] = relationship()
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    url: Mapped[Optional[str]] = mapped_column()
    logo_url: Mapped[Optional[str]] = mapped_column()
