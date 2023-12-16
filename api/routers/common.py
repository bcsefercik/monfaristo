import sys
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models.common import Currency
from models.user import User
from passlib.context import CryptContext
from pydantic import BaseModel
from routers.auth import get_current_user
from settings.database import SessionLocal, engine
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
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"bcs": "latte"}
