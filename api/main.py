import models
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, common, journal
from settings.database import engine

app = FastAPI()


# TODO: move these to env vars
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(common.router)
app.include_router(journal.router)
