from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_, or_
from datetime import date

from app.model.entry_model import Entry
from app.model.contest_participation_model import ContestParticipation

async def create_entry(db: AsyncSession, contest_id: int, user_id: int, content: str) -> Entry:
    entry = Entry(contest_id=contest_id, user_id=user_id, content=content)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

async def get_entry_by_user_id(db: AsyncSession, user_id: int) -> list[Entry]:
    stmt = select(Entry).where(Entry.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_entry_by_entry_id(db: AsyncSession, entry_id: int) -> Entry:
    stmt = select(Entry).where(Entry.id == entry_id).order_by(Entry.rating.desc())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_entry_by_contest_id(db: AsyncSession, contest_id: int) -> list[Entry]:
    stmt = select(Entry).where(Entry.contest_id == contest_id).order_by(Entry.rating.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_entry_by_user_and_contest_id(db: AsyncSession, user_id: int, contest_id: int) -> Entry | None:
    stmt = select(Entry).where(Entry.user_id==user_id, Entry.contest_id==contest_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_random_two_entries_excluding_user(db: AsyncSession, contest_id: int, user_id: int) -> list[Entry]:
    stmt = (
        select(Entry)
        .where(
            Entry.contest_id==contest_id,
            Entry.user_id!=user_id
        )
        .order_by(func.random())
        .limit(2)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_ranking_entries(db: AsyncSession, contest_id: int, offset: int, limit: int) -> list[Entry]:
    stmt = (
        select(Entry)
        .join(
            ContestParticipation,
            (ContestParticipation.contest_id == Entry.contest_id)
            & (ContestParticipation.user_id == Entry.user_id)
        )
        .where(
            Entry.contest_id == contest_id,
            ContestParticipation.has_submitted_entry.is_(True),
            ContestParticipation.evaluation_count >= 50,
        )
        .order_by(Entry.rating.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def count_entries_by_contest_id(db: AsyncSession, contest_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Entry)
        .where(
            Entry.contest_id==contest_id,
            ContestParticipation.has_submitted_entry.is_(True),
            ContestParticipation.evaluation_count >= 50,
            (ContestParticipation.contest_id==Entry.contest_id)
            & (ContestParticipation.user_id==Entry.user_id)
        ))
    result = await db.execute(stmt)
    return result.scalar_one()

async def count_entries_above_me(db: AsyncSession, contest_id: int, my_rating: float, user_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Entry)
        .where(
            Entry.contest_id==contest_id,
            ContestParticipation.has_submitted_entry.is_(True),
            ContestParticipation.evaluation_count >= 50,
            (ContestParticipation.contest_id==Entry.contest_id)
            & (ContestParticipation.user_id==Entry.user_id),
            or_(
                Entry.rating > my_rating,
                and_(
                    Entry.rating == my_rating,
                    Entry.id < user_id
                )
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()

async def update_entry(
        db: AsyncSession,
        entry: Entry,
        user_id: int | None = None,
        contest_id: int | None = None,
        content: str | None = None,
        rating: float | None = None,
        rd: float | None = None,
        volatility: float | None = None,
        comparisons_count: int | None = None,
        wins: int | None = None,
        losses: int | None = None,
) -> Entry:
    if user_id is not None:
        entry.user_id = user_id
    if contest_id is not None:
        entry.contest_id = contest_id
    if content is not None:
        entry.content = content
    if rating is not None:
        entry.rating = rating
    if rd is not None:
        entry.rd = rd
    if volatility is not None:
        entry.volatility = volatility
    if comparisons_count is not None:
        entry.comparisons_count = comparisons_count
    if wins is not None:
        entry.wins = wins
    if losses is not None:
        entry.losses = losses
    
    await db.commit()
    await db.refresh(entry)
    ##await db.flush()
    return entry

async def delete_entry(db: AsyncSession, entry: Entry) -> None:
    await db.delete(entry)
    await db.flush()


