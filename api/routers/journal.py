import datetime
import sys
from audioop import avg
from calendar import c
from locale import currency
from re import M
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models.common import Currency, Market, Platform, Ticker
from models.cumulative_ticker_holding import (
    CumulativeTickerHolding,
    CumulativeTickerHoldingFilter,
    CumulativeTickerHoldingOrderingOptions,
    CumulativeTickerHoldingRepository,
)
from models.journal import InvestmentAccount, Transaction
from models.user import User
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from routers.auth import get_current_user
from routers.utils import generate_ordering_dict
from settings.database import SessionLocal, engine, get_db
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/journal", tags=["journal"], responses={401: {"user": "Not authorized"}}
)


class InvestmentAccountCreateModel(BaseModel):
    title: str
    owner_id: int


@router.post("/account")
async def create_account(
    investment_account: InvestmentAccountCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_code=status.HTTP_201_CREATED,
):
    created_account = InvestmentAccount(**investment_account.model_dump())
    db.add(created_account)
    db.commit()
    db.refresh(created_account)
    return created_account


@router.get("/accounts")
async def get_accounts(
    q: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(InvestmentAccount)

    if q:
        query = query.filter(InvestmentAccount.title.like(f"%{q}%"))

    return query.all()


@router.get("/account/{investment_account_id}")
async def get_currency(
    investment_account_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(InvestmentAccount)
        .filter(InvestmentAccount.id == investment_account_id)
        .first()
    )


@router.delete("/account/{investment_account_id}")
async def deactivate_account(
    investment_account_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(InvestmentAccount).filter(
        InvestmentAccount.id == investment_account_id
    ).update({"is_active": False})
    db.commit()


class TransactionCreateModel(BaseModel):
    ticker_id: int = Field(gt=0)
    price: float = Field(ge=0)
    count: float = Field(gt=0)
    commission: float = Field(ge=0)
    type: Transaction.Type
    investment_account_id: int = Field(gt=0)
    platform_id: int = Field(gt=0)
    executed_at: datetime.datetime = Field(default=datetime.datetime.utcnow())
    executed_by_id: Optional[int] = Field(default=None)
    description: str = Field(default="")
    notes: str = Field(default="")
    time_frame: Optional[Transaction.TimeFrame] = Field(default=None)


@router.post("/transaction", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate_transaction = transaction.model_dump()

    # TODO: if user is admin, permit them to override executed_by_id
    if candidate_transaction["executed_by_id"] is None:
        candidate_transaction["executed_by_id"] = user["id"]
    with db.begin():
        cumulative_ticker_holding = (
            db.query(CumulativeTickerHolding)
            .filter(
                CumulativeTickerHolding.ticker_id == candidate_transaction["ticker_id"]
            )
            .filter(
                CumulativeTickerHolding.investment_account_id
                == candidate_transaction["investment_account_id"]
            )
            .filter(CumulativeTickerHolding.is_completed == False)
            .first()
        )

        if cumulative_ticker_holding is None:
            cumulative_ticker_holding = CumulativeTickerHolding(
                ticker_id=candidate_transaction["ticker_id"],
                investment_account_id=candidate_transaction["investment_account_id"],
            )
            db.add(cumulative_ticker_holding)
            db.flush()
            db.refresh(cumulative_ticker_holding)

        candidate_transaction[
            "cumulative_ticker_holding_id"
        ] = cumulative_ticker_holding.id

        created_transaction = Transaction(**candidate_transaction)
        db.add(created_transaction)
        db.flush()

        cumulative_ticker_holding.add_transaction(db, created_transaction)

    db.refresh(created_transaction)
    db.refresh(cumulative_ticker_holding)

    return created_transaction


@router.get("/transactions")
async def get_transactions(
    q: str | None = None,
    investment_account: int | None = None,
    executed_by: int | None = None,
    is_active: bool | None = None,
    type: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)

    if q:
        query = query.filter(
            or_(
                Transaction.ticker_id == Ticker.code.like(f"%{q}%"),
                # Transaction.ticker.code.like(f"%{q}%"),
                # Transaction.ticker.market.code.like(f"%{q}%"),
                # Transaction.ticker.market.title.like(f"%{q}%"),
                # Transaction.ticker.market.currency.code.like(f"%{q}%"),
            )
        )

    if investment_account:
        query = query.filter(Transaction.investment_account_id == investment_account)

    if executed_by:
        query = query.filter(Transaction.executed_by_id == executed_by)

    if is_active:
        query = query.filter(Transaction.is_active == is_active)

    if type:
        query = query.filter(Transaction.type == type)

    return query.all()


@router.get("/transaction/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


class CumulativeTickerHoldingsSchema(BaseModel):
    class TickerSchema(BaseModel):
        class MarketSchema(BaseModel):
            class CurrencySchema(BaseModel):
                id: int
                title: str
                code: str
                symbol: str

                class Config:
                    from_attributes = True

            id: int
            title: str
            code: str
            currency: CurrencySchema

            class Config:
                from_attributes = True

        id: int
        title: str
        code: str
        market: MarketSchema

        class Config:
            from_attributes = True

    class InvestmentAccountSchema(BaseModel):
        class UserSchema(BaseModel):
            id: int
            email: str
            first_name: str
            last_name: str

            class Config:
                from_attributes = True

        id: int
        title: str
        owner: UserSchema

        class Config:
            from_attributes = True

    id: int
    ticker: TickerSchema
    investment_account: InvestmentAccountSchema
    avg_cost: float
    count: float
    total_buys: float
    total_buy_amount: float
    total_sells: float
    total_sell_amount: float
    total_commission_cost: float
    is_completed: bool
    first_transaction_at: datetime.datetime
    last_transaction_at: Optional[datetime.datetime] = None
    adjusted_avg_cost: Optional[float] = None
    pnl_amount: Optional[float] = None
    pnl_ratio: Optional[float] = None

    class Config:
        from_attributes = True


@router.get(
    "/cumulative_ticker_holdings",
    response_model=List[CumulativeTickerHoldingsSchema],
)
async def get_cumulative_ticker_holdings(
    investment_account_id: int | None = None,
    ticker_id: int | None = None,
    is_completed: bool | None = None,
    ordering: str | None = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    repo = CumulativeTickerHoldingRepository(db)

    ordering_dict = generate_ordering_dict(
        ordering,
        valid_params=CumulativeTickerHoldingOrderingOptions.model_fields.keys(),
    )
    ordering_options = CumulativeTickerHoldingOrderingOptions(**ordering_dict)

    filter = CumulativeTickerHoldingFilter(
        investment_account_id=investment_account_id,
        ticker_id=ticker_id,
        is_completed=is_completed,
    )

    return repo.get_all(filter=filter, ordering=ordering_options)
