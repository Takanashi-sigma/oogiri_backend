from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone
from app.model.jwt_login_modle import RefreshToken
from app.core.security import hash_password


async def store_refresh_token(db: AsyncSession, user_id: int, jti: str, raw_token: str, expires_at):
    refresh_token = RefreshToken(
        user_id=user_id, 
        jti=jti,
        hashed_token=hash_password(raw_token),
        expires_at=expires_at
        )
    db.add(refresh_token)
    await db.commit()
    return refresh_token


async def get_refrsh_token(db: AsyncSession, jti: str):
    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, jti: str):
    await db.execute(delete(RefreshToken).where(RefreshToken.jti == jti))
    await db.commit()


async def purge_expired(db: AsyncSession):
    await db.execute(delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(timezone.utc)))
    await db.commit()


