from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import date

from app.model.contest_model import Contest, ContestStatus

async def create_contest(db: AsyncSession, title: str, status: ContestStatus, prompt: str, start_at: date, end_at: date, thumbnail_url: str) -> Contest:
    contest = Contest(
        title=title,
        prompt=prompt,
        status=status,
        start_at=start_at,
        end_at=end_at,
        thumbnail_url=thumbnail_url
    )
    db.add(contest)
    await db.commit()
    await db.refresh(contest)
    return contest

async def get_contests(db: AsyncSession) -> list[Contest]:
    stmt = select(Contest).order_by(Contest.start_at.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contest_by_id(db: AsyncSession, contest_id: int) -> Contest | None:
    stmt = select(Contest).where(Contest.id==contest_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_contest(
        db: AsyncSession, 
        contest: Contest,
        title: str | None = None,
        prompt: str | None = None,
        status: ContestStatus | None = None,
        start_at: date | None = None,
        end_at: date | None = None
    ) -> Contest:
    if title is not None:
        contest.title = title
    if prompt is not None:
        contest.prompt = prompt
    if status is not None:
        contest.status = status
    if start_at is not None:
        contest.start_at = start_at
    if end_at is not None:
        contest.end_at = end_at
    await db.commit()
    await db.refresh(contest)
    return contest

async def get_contests_of_draft_or_open(db: AsyncSession) -> list[Contest]:
    stmt = select(Contest).where(Contest.status!=ContestStatus.closed)
    result = await db.execute(stmt)
    return result.scalars().all()

async def delete_contest(db: AsyncSession, contest: Contest) -> None:
    await db.delete(contest)
    await db.flush()