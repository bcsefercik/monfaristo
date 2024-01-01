import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Response, status
from models.common import (
    Currency,
    LiquidAssetAccount,
    LiquidAssetTransaction,
    Market,
    Platform,
    Ticker,
)
from pydantic import BaseModel, Field
from requests import get
from routers.auth import get_current_user
from settings.database import SessionLocal, get_db, get_or_create
from sqlalchemy import null, or_
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="",
    tags=["common"],
    responses={status.HTTP_401_UNAUTHORIZED: {"user": "Not authorized"}},
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
async def delete_market(
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
        .filter(
            Market.code == ticker.market_code.upper(), Market.currency_id == currency.id
        )
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
    ticker_code: str,
    market_code: str,
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


class LiquidAssetAccountCreateModel(BaseModel):
    title: str = Field(default=None, nullable=True)
    platform_id: int = Field(gt=0)
    currency_id: int = Field(gt=0)
    owner_id: int = Field(gt=0)


@router.post("/liquid_asset_account")
async def create_liquid_asset_account(
    liquid_asset_account: LiquidAssetAccountCreateModel,
    response: Response,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    liquid_asset_dict = liquid_asset_account.model_dump()

    created_liquid_asset, created = get_or_create(
        db, LiquidAssetAccount, **liquid_asset_dict
    )

    db.commit()
    db.refresh(created_liquid_asset)

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK

    return created_liquid_asset


@router.get("/liquid_asset_account")
async def get_liquid_asset_account(
    platform_id: int,
    currency_id: int,
    owner_id: int,
    title: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(LiquidAssetAccount)
        .filter(LiquidAssetAccount.platform_id == platform_id)
        .filter(LiquidAssetAccount.currency_id == currency_id)
        .filter(LiquidAssetAccount.owner_id == owner_id)
    )

    if title is None:
        query = query.filter(LiquidAssetAccount.title == title)
    else:
        query = query.like(f"%{title}%")

    return query.first()


class LiquidAssetTransactionCreateModel(BaseModel):
    liquid_asset_account_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    type: LiquidAssetTransaction.Type = Field(
        default=LiquidAssetTransaction.Type.DEPOSIT
    )
    executed_at: datetime.datetime = Field(default=datetime.datetime.utcnow)
    description: Optional[str] = Field(default=None)


@router.post("/liquid_asset/transaction")
async def create_liquid_asset_transaction(
    liquid_asset_transaction: LiquidAssetTransactionCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_code=status.HTTP_201_CREATED,
):
    with db.begin():
        created_liquid_asset_transaction = LiquidAssetTransaction(
            **liquid_asset_transaction.model_dump()
        )

        db.add(created_liquid_asset_transaction)
        db.flush()
        db.refresh(created_liquid_asset_transaction)

        liquid_asset = (
            db.query(LiquidAssetAccount)
            .filter(
                LiquidAssetAccount.id
                == liquid_asset_transaction.liquid_asset_account_id
            )
            .first()
        )
        created_liquid_asset_transaction.liquid_asset_account.add_transaction(
            db, created_liquid_asset_transaction
        )

    db.refresh(created_liquid_asset_transaction)
    db.refresh(created_liquid_asset_transaction.liquid_asset_account)

    return created_liquid_asset_transaction
