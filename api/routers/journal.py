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
from models.journal import Transaction
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
    prefix="", tags=["journal"], responses={401: {"user": "Not authorized"}}
)
