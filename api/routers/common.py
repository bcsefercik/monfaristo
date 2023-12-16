import sys
from datetime import datetime, timedelta
from typing import Optional

import ipdb
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models.common import Currency
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
    prefix="/common", tags=["common"], responses={401: {"user": "Not authorized"}}
)


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


class CurrencyCreateModel(BaseModel):
    title: str
    code: str = Field(min_length=3)
    symbol: Optional[str] = Field(
        min_length=1, description="Currency symbol", default=None
    )


@router.post("/currency")
async def creatge_currency(
    currency: CurrencyCreateModel,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    created_currency = Currency(**currency.model_dump())
    db.add(created_currency)
    db.commit()
    db.refresh(created_currency)
    return created_currency
