from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from typing import Annotated

from app.core.database import get_db
from app.service.jwt_login_service import issue_tokens, refresh_tokens
from app.service.user_service import authenticate_user
from app.core.security import decode_access, decode_refresh 
from app.model.user_model import User


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class LoginJSON(BaseModel):
    email: EmailStr
    password: str

class RefreshInput(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    id: int
    email: EmailStr

@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
    ):
    user = await authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="認証失敗")
    access, refresh = await issue_tokens(db, user.id)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.post("/login_json", response_model=TokenResponse)
async def login_json(
    payload: Annotated[LoginJSON, Body()], 
    db: AsyncSession = Depends(get_db)
    ):
    user = await authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="認証失敗")
    access, refresh = await issue_tokens(db, user.id)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshInput, 
    db: AsyncSession = Depends(get_db)
    ):
    result = await refresh_tokens(db, payload.refresh_token, decode_refresh)
    if not result:
        raise HTTPException(status_code=401, detail="無効なトークンです。")
    access, new_refresh = result
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}


@router.get("/me", response_model=MeResponse)
async def me(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
    ):
    try:
        data = decode_access(token)
        user_id = int(data["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="トークン不正")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザなし")
    return {"id": user.id, "email": user.email}


