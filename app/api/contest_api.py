from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.service.contest_service import create_contest_with_validation, list_contests, get_contest_by_contest_id, refresh_active_contest_status, delete_contest_by_contest_id
from app.schema.contest_schema import ContestRead, ContestCreate
from app.core.security import require_admin
from app.model.user_model import User

router = APIRouter(prefix="/contests", tags=["contests"])

@router.post("/admin", response_model=ContestRead)
async def create_contest(data: ContestCreate, db: AsyncSession = Depends(get_db), admin_user: User = Depends(require_admin)):
    result = await create_contest_with_validation(db=db, title=data.title, prompt=data.prompt, start_at=data.start_at, end_at=data.end_at, thumbnail_url=data.thumbnail_url)

    return result

@router.get("", response_model=list[ContestRead])
async def get_contest_list(db: AsyncSession = Depends(get_db)):
    await refresh_active_contest_status(db=db)
    result = await list_contests(db=db)
    return result

@router.get("/{contest_id}", response_model=ContestRead)
async def get_contest(contest_id: int, db: AsyncSession = Depends(get_db)):
    await refresh_active_contest_status(db=db)
    result = await get_contest_by_contest_id(db=db, contest_id=contest_id)
    return result

@router.delete("{contest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contest_by_admin(contest_id: int, db: AsyncSession = Depends(get_db)):
    await delete_contest_by_contest_id(db=db, contest_id=contest_id)


