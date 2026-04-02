from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import date

from app.model.contest_participation_model import ContestParticipation

async def create_contest_participation(db: AsyncSession, contest_id: int, user_id: int) -> ContestParticipation:
    contest_participation=ContestParticipation(contest_id=contest_id, user_id=user_id)
    db.add(contest_participation)
    await db.commit()
    await db.refresh(contest_participation)
    return contest_participation

async def get_contest_participations_by_user_id(db: AsyncSession, user_id: int) -> list[ContestParticipation]:
    stmt = select(ContestParticipation).where(ContestParticipation.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_contest_participation_by_contest_id(db: AsyncSession, contest_id: int) -> list[ContestParticipation]:
    stmt = select(ContestParticipation).where(ContestParticipation.contest_id == contest_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_contest_participation_by_user_and_contest_id(db: AsyncSession, user_id: int, contest_id: int) -> ContestParticipation | None:
    stmt = select(ContestParticipation).where(ContestParticipation.user_id == user_id, ContestParticipation.contest_id == contest_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_contest_participation(
        db: AsyncSession,
        contest_participation: ContestParticipation,
        contest_id: int | None = None,
        user_id: int | None = None,
        has_submitted_entry: bool | None = None,
        evaluation_count: int | None = None
) -> ContestParticipation:
    if contest_id is not None:
        contest_participation.contest_id = contest_id
    if user_id is not None:
        contest_participation.user_id = user_id
    if has_submitted_entry is not None:
        contest_participation.has_submitted_entry = has_submitted_entry
    if evaluation_count is not None:
        contest_participation.evaluation_count = evaluation_count
    
    #await db.commit()
    #await db.refresh(contest_participation)
    await db.flush()
    return contest_participation

async def delete_contest_participation(db: AsyncSession, contest_participation: ContestParticipation) -> None:
    await db.delete(contest_participation)
    await db.flush()

