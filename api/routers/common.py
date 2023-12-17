import sys
from calendar import c
from datetime import datetime, timedelta
from locale import currency
from re import M
from typing import Optional
from venv import create

import ipdb
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models.common import Currency, Market, Platform, Ticker
from models.user import User
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from routers.auth import get_current_user
from settings.database import SessionLocal, engine
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="", tags=["common"], responses={401: {"user": "Not authorized"}}
)


class CurrencyCreateModel(BaseModel):
    title: str
    code: str = Field(min_length=3)
    symbol: Optional[str] = Field(
        min_length=1, description="Currency symbol", default=None
    )


@router.post("/currency")
async def create_currency(
    currency: CurrencyCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    created_currency = Currency(**currency.model_dump())
    db.add(created_currency)
    db.commit()
    db.refresh(created_currency)
    return created_currency


@router.get("/currencies")
async def get_currencies(
    q: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Currency)

    if q:
        query = query.filter(
            or_(Currency.title.like(f"%{q}%"), Currency.code.like(f"%{q}%"))
        )

    return query.all()


@router.get("/currency/{currency_code}")
async def get_currency(
    currency_code: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Currency).filter(Currency.code == currency_code.upper()).first()


@router.delete("/currency/{currency_id}")
async def delete_currency(
    currency_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Currency).filter(Currency.id == currency_id).delete()


class PlatformCreateModel(BaseModel):
    title: str
    description: Optional[str] = Field(description="Logo image URL", default=None)
    url: Optional[str] = Field(description="Web site URL", default=None)
    logo_url: Optional[str] = Field(description="Logo image URL", default=None)


@router.post("/platform")
async def create_platform(
    platform: PlatformCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    created_platform = Platform(**platform.model_dump())
    db.add(created_platform)
    db.commit()
    db.refresh(created_platform)
    return created_platform


@router.get("/platforms")
async def get_platforms(
    q: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Platform)

    if q:
        query = query.filter(
            or_(Platform.title.like(f"%{q}%"), Platform.url.like(f"%{q}%"))
        )

    return query.all()


@router.get("/platform/{platform_id}")
async def get_platform(
    platform_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Platform).filter(Platform.id == platform_id).first()


@router.delete("/platform/{platform_id}")
async def delete_platform(
    platform_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Platform).filter(Platform.id == platform_id).delete()


class MarketCreateModel(BaseModel):
    title: str
    code: str
    currency_code: str
    description: Optional[str] = Field(default=None)


@router.post("/market")
async def create_market(
    market: MarketCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate_market = market.model_dump()

    candidate_market["currency_id"] = (
        db.query(Currency)
        .filter(Currency.code == market.currency_code.upper())
        .first()
        .id
    )
    candidate_market.pop("currency_code")

    created_market = Market(**candidate_market)

    db.add(created_market)
    db.commit()
    db.refresh(created_market)

    return created_market


@router.get("/markets")
async def get_markets(
    q: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Market)

    if q:
        query = query.filter(
            or_(Market.title.like(f"%{q}%"), Market.code.like(f"%{q}%"))
        )

    return query.all()


@router.get("/market/{market_code}")
async def get_market(
    market_code: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Market).filter(Market.code == market_code).first()


@router.delete("/market/{market_code}")
async def delete_platform(
    market_code: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Market).filter(Market.code == market_code).delete()


class TickerCreateModel(BaseModel):
    title: str
    code: str
    market_code: str
    currency_code: str
    is_active: Optional[bool] = Field(default=True)
    url: Optional[str] = Field(default=None)
    logo_url: Optional[str] = Field(default=None)


@router.post("/ticker")
async def create_ticker(
    ticker: TickerCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate_ticker = ticker.model_dump()

    currency = db.query(Currency).filter(Currency.code == ticker.currency_code).first()
    candidate_ticker.pop("currency_code")

    candidate_ticker["market_id"] = (
        db.query(Market)
        .filter(Market.code == ticker.market_code, Market.currency_id == currency.id)
        .first()
        .id
    )

    candidate_ticker.pop("market_code")

    created_ticker = Ticker(**candidate_ticker)

    db.add(created_ticker)
    db.commit()
    db.refresh(created_ticker)

    return created_ticker


@router.get("/tickers")
async def get_tickers(
    q: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Ticker)

    if q:
        query = query.filter(
            or_(Ticker.title.like(f"%{q}%"), Ticker.code.like(f"%{q}%"))
        )

    return query.all()


@router.get("/ticker/{ticker_code}/{market_code}")
async def get_ticker(
    ticker_code: int,
    market_code: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    market = db.query(Market).filter(Market.code == market_code).first()

    return (
        db.query(Ticker)
        .filter(Ticker.code == ticker_code, Ticker.market_id == market.id)
        .first()
    )


@router.delete("/ticker/{ticker_code}/{market_code}")
async def delete_ticker(
    ticker_code: int,
    market_code: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    market = db.query(Market).filter(Market.code == market_code).first()

    return (
        db.query(Ticker)
        .filter(Ticker.code == ticker_code, Ticker.market_id == market.id)
        .delete()
    )
