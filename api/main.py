from fastapi import FastAPI, Depends
import models
from settings.database import engine
from routers import auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)