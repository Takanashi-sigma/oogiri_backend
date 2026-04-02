from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.core.database import get_db
from app.service.contest_participation_service import get_contest_participations_by_user_id, get_contest_participation_by_contest_id, delete_contest_participation_by_contest_id, get_my_contest_participation
from app.schema.contest_participation_schema import ContestParticipationRead
from app.model.user_model import User

router = APIRouter(prefix="/contest-participations", tags=["contest-participations"])

@router.get("/me", response_model=list[ContestParticipationRead])
async def get_my_contest_participations(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await get_contest_participations_by_user_id(db=db, user_id=user.id)
    return result

@router.get("/{contest_id}/me", response_model=ContestParticipationRead)
async def get_contest_participation(contest_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await get_my_contest_participation(user_id=user.id, contest_id=contest_id, db=db)
    return result

@router.get("", response_model=list[ContestParticipationRead])
async def get_contest_participations(contest_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_contest_participation_by_contest_id(db=db, contest_id=contest_id)
    return result

@router.delete("{contest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contest_by_admin(contest_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await delete_contest_participation_by_contest_id(db=db, contest_id=contest_id, user_id=user.id)

