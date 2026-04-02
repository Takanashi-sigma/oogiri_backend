from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException
from app.core.database import get_db
from app.crud.user_crud import get_user_by_id
from app.model.user_model import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:

    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os, uuid


ACCESS_SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

def create_access_token(sub: str | int) -> str:
    now = datetime.now(timezone.utc)
    playload = {
        "sub": str(sub),
        "iat": now,
         "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
         }
    
    return jwt.encode(playload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(sub: str |int, jti: str):
    now = datetime.now(timezone.utc)
    playload = {
        "sub": str(sub),
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
         } 
    
    return jwt.encode(playload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_access(token: str) -> dict:

    return jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])


def decode_refresh(token: str) -> dict:

    return jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])

def new_jti() -> str:
    return uuid.uuid4().hex

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):  
    try:
        payload=decode_access(token=token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token payload")
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(status_code=401, detail="invalid token payload")
    user = await get_user_by_id(db=db, user_id=int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="user not found")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="admin only")
    return user


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)