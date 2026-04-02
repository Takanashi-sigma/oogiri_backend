import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.model.user_model import User
from app.core.security import get_password_hash


async def seed_users(count: int = 50) -> None:
    async with AsyncSessionLocal() as db:
        created = 0

        for i in range(1, count + 1):
            email = f"dummy{i}@example.com"

            result = await db.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user is not None:
                continue

            user = User(
                email=email,
                hashed_password=get_password_hash("test1234"),
                is_active=True,
                is_admin=False,
            )
            db.add(user)
            created += 1

        await db.commit()
        print(f"{created} users inserted.")
        print("password for all dummy users: test1234")


if __name__ == "__main__":
    asyncio.run(seed_users())