import datetime
import sys
from calendar import c
from locale import currency
from re import M
from typing import Optional
from venv import create

import ipdb
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models.common import Currency, Market, Platform, Ticker
from models.journal import Account, CumulativeTickerHolding, Transaction
from models.user import User
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from routers.auth import get_current_user
from settings.database import SessionLocal, engine, get_db
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/journal", tags=["journal"], responses={401: {"user": "Not authorized"}}
)


class AccountCreateModel(BaseModel):
    title: str
    owner_id: int


@router.post("/account")
async def create_account(
    account: AccountCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_code=status.HTTP_201_CREATED,
):
    created_account = Account(**account.model_dump())
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
    query = db.query(Account)

    if q:
        query = query.filter(Account.title.like(f"%{q}%"))

    return query.all()


@router.get("/account/{account_id}")
async def get_currency(
    account_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Account).filter(Account.id == account_id).first()


@router.delete("/account/{account_id}")
async def deactivate_account(
    account_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(Account).filter(Account.id == account_id).update({"is_active": False})
    db.commit()


class TransactionCreateModel(BaseModel):
    ticker_id: int = Field(gt=0)
    price: float = Field(gt=0)
    count: float = Field(gt=0)
    commission: float = Field(ge=0)
    type: Transaction.Type
    account_id: int = Field(gt=0)
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

    cumulative_ticker_holding = (
        db.query(CumulativeTickerHolding)
        .filter(CumulativeTickerHolding.ticker_id == Transaction.ticker_id)
        .filter(CumulativeTickerHolding.account_id == Transaction.account_id)
        .filter(CumulativeTickerHolding.is_completed == False)
        .first()
    )

    if cumulative_ticker_holding is None:
        cumulative_ticker_holding = CumulativeTickerHolding(
            ticker_id=candidate_transaction["ticker_id"],
            account_id=candidate_transaction["account_id"],
        )
        db.add(cumulative_ticker_holding)
        db.commit()
        db.refresh(cumulative_ticker_holding)

    created_transaction = Transaction(**candidate_transaction)
    db.add(created_transaction)
    db.commit()

    cumulative_ticker_holding.add_transaction(created_transaction)
    db.commit()

    db.refresh(created_transaction)
    db.refresh(cumulative_ticker_holding)

    return created_transaction


@router.get("/transactions")
async def get_transactions(
    q: str | None = None,
    account: int | None = None,
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

    if account:
        query = query.filter(Transaction.account_id == account)

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
