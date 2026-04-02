from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schema.user_schema import UserRead, UserCreate
from app.service.user_service import register_user
from app.crud.user_crud import get_user_by_email

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await get_user_by_email(db, data.email)
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="すでに使用されたメールアドレスです")
    created = await register_user(db, email=data.email, plain_password=data.password)
    return created


