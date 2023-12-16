import models
from fastapi import Depends, FastAPI
from routers import auth, common
from settings.database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(common.router)
