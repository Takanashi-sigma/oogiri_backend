from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.crud.contest_participation_crud import create_contest_participation, get_contest_participation_by_contest_id, get_contest_participations_by_user_id, update_contest_participation, get_contest_participation_by_user_and_contest_id, delete_contest_participation, get_contest_participation_by_user_and_contest_id
from app.model.contest_participation_model import ContestParticipation
from app.crud.entry_crud import get_entry_by_user_and_contest_id

async def participate_contest(db: AsyncSession, user_id: int, contest_id: int) -> ContestParticipation:
    has_participated = await get_contest_participation_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if has_participated:
        raise HTTPException(status_code=400, detail="participation only once")

    result = await create_contest_participation(db=db, contest_id=contest_id, user_id=user_id)
    return result

async def get_my_contest_participations(db: AsyncSession, user_id: int) -> list[ContestParticipation]:
    result = await get_contest_participations_by_user_id(db=db, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="contest particiption not found")
    return result

async def get_contest_participations(db: AsyncSession, contest_id: int) -> list[ContestParticipation]:
    result = await get_contest_participation_by_contest_id(db=db, contest_id=contest_id)
    if not result:
        raise HTTPException(status_code=404, detail="contest participtions not found")
    return result

async def get_my_contest_participation(db: AsyncSession, contest_id: int, user_id: int) -> ContestParticipation:
    result = await get_contest_participation_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if not result:
        raise HTTPException(status_code=404, detail="not found contest_participation")
    return result

async def update_evaluation_count(db: AsyncSession, user_id: int, contest_id: int) -> ContestParticipation:
    contest_participation = await get_contest_participation_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if not contest_participation:
        raise HTTPException(status_code=404, detail="contest_participation not found")
    entry = await get_entry_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")
    contest_participation.evaluation_count = contest_participation.evaluation_count + 1
    return await update_contest_participation(
        db=db,
        contest_participation=contest_participation,
        evaluation_count=contest_participation.evaluation_count,
        has_submitted_entry=contest_participation.has_submitted_entry
    )

async def delete_contest_participation_by_contest_id(db: AsyncSession, contest_id: int, user_id: int) -> None:
    contest_participation = await get_contest_participation_by_user_and_contest_id(db=db, contest_id=contest_id, user_id=user_id)
    if not contest_participation:
        raise HTTPException(status_code=404, detail="contest_participation not found")
    await delete_contest_participation(db=db, contest=contest_participation)
    await db.commit()


