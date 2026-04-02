from sqlalchemy.ext.asyncio import AsyncSession
from app.model.user_model import User
from sqlalchemy import select

async def create_user_in_db(db: AsyncSession, email: str, hashed_password: str, is_active: bool = True, is_admin: bool = False, **kwargs):
    new_user = User(email=email, hashed_password=hashed_password, is_active=is_active, is_admin=is_admin, **kwargs)
    db.add(new_user)
    await db.flush()
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_email(db: AsyncSession, email: str):
    q = await db.execute(select(User).where(User.email == email))
    return q.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.get(User, user_id)
    return result