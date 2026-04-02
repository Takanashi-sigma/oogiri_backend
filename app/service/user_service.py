from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.model.user_model import User
from app.core.security import hash_password, verify_password
from app.crud.user_crud import create_user_in_db, get_user_by_email, get_user_by_id

async def register_user(db, email: str, plain_password: str, **other):
    # 1) 必要ならここでパスワード強度チェック（長さ等）
    # 2) ハッシュ化
    hashed = hash_password(plain_password)

    # 3) DB保存（平文は渡さない）
    user = await create_user_in_db(db, email=email, hashed_password=hashed, **other)
    return user

async def authenticate_user(db, email: str, plain_password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(plain_password, user.hashed_password):
        return None
    return user

async def get_user_by_id_with_validation(db: AsyncSession, user_id: int) -> User:
    result = await  get_user_by_id(db=db, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="user not found")
    return result