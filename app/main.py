from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import app.model
from app.scheduler.contest_scheduler import start_scheduler

from app.api.jwt_login_api import router as jwt_login_router
from app.api.user_api import router as user_router
from app.api.contest_api import router as contest_router
from app.api.entry_api import router as entry_router
from app.api.contest_participation_api import router as contest_participation_router
from app.api.comparison_api import router as comparison_router

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
async def on_startup():
    start_scheduler()

app.include_router(jwt_login_router)
app.include_router(user_router)
app.include_router(contest_router)
app.include_router(entry_router)
app.include_router(contest_participation_router)
app.include_router(comparison_router)
