from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.crud.contest_crud import (
    create_contest,
    get_contest_by_id,
    get_contests,
    update_contest,
    get_contests_of_draft_or_open,
    delete_contest,
)
from app.model.contest_model import ContestStatus, Contest

from datetime import date


def calculate_contest_status(start_at: date, end_at: date, today: date | None = None) -> ContestStatus:
    today = today or date.today()

    if today < start_at:
        return ContestStatus.draft
    if start_at <= today <= end_at:
        return ContestStatus.open
    return ContestStatus.closed


async def create_contest_with_validation(
    db: AsyncSession,
    title: str,
    prompt: str,
    start_at: date,
    end_at: date,
    thumbnail_url: str,
):
    if start_at > end_at:
        raise HTTPException(status_code=400, detail="start_at must be before end_at")

    status = calculate_contest_status(start_at=start_at, end_at=end_at)

    result = await create_contest(
        db,
        title=title,
        status=status,
        prompt=prompt,
        start_at=start_at,
        end_at=end_at,
        thumbnail_url=thumbnail_url,
    )
    return result


async def get_contest_by_contest_id(db: AsyncSession, contest_id: int) -> Contest:
    contest = await get_contest_by_id(db=db, contest_id=contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="contest not found")
    return contest


async def update_contest_with_validation(
    db: AsyncSession,
    contest_id: int,
    title: str | None = None,
    prompt: str | None = None,
    start_at: date | None = None,
    end_at: date | None = None,
):
    contest = await get_contest_by_id(db=db, contest_id=contest_id)
    if contest is None:
        raise HTTPException(status_code=404, detail="contest not found")

    new_start_at = start_at if start_at is not None else contest.start_at
    new_end_at = end_at if end_at is not None else contest.end_at

    if new_start_at > new_end_at:
        raise HTTPException(status_code=400, detail="start_at must be on or before end_at")

    new_status = calculate_contest_status(start_at=new_start_at, end_at=new_end_at)

    return await update_contest(
        db=db,
        contest=contest,
        title=title,
        prompt=prompt,
        status=new_status,
        start_at=new_start_at,
        end_at=new_end_at,
    )


async def list_contests(db: AsyncSession):
    result = await get_contests(db=db)
    return result


async def refresh_active_contest_status(db: AsyncSession) -> list[Contest]:
    contests = await get_contests_of_draft_or_open(db=db)

    updated_contests = []

    for contest in contests:
        new_status = calculate_contest_status(start_at=contest.start_at, end_at=contest.end_at)
        if contest.status != new_status:
            contest.status = new_status
            updated_contests.append(contest)

    if updated_contests:
        await db.commit()
        for contest in updated_contests:
            await db.refresh(contest)
    return updated_contests


async def delete_contest_by_contest_id(db: AsyncSession, contest_id: int) -> None:
    contest = await get_contest_by_id(db=db, contest_id=contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="contest not found")
    await delete_contest(db=db, contest=contest)
    await db.commit()