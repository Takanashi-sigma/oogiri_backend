from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import date

from app.model.comparison_model import Comparison

async def create_comparison(
        db: AsyncSession,
        contest_id: int,
        voter_user_id: int,
        entry_a_id: int,
        entry_b_id: int,
        chosen_entry_id: int,
        entry_a_rating_before: float,
        entry_b_rating_before: float,
        entry_a_rd_before: float,
        entry_b_rd_before: float,
        entry_a_volatility_before: float,
        entry_b_volatility_before: float,
        entry_a_rating_after: float,
        entry_b_rating_after: float,
        entry_a_rd_after: float,
        entry_b_rd_after: float,
        entry_a_volatility_after: float,
        entry_b_volatility_after: float
) -> Comparison:
    comparison = Comparison(
        contest_id=contest_id,
        voter_user_id=voter_user_id,
        entry_a_id=entry_a_id,
        entry_b_id=entry_b_id,
        chosen_entry_id=chosen_entry_id,
        entry_a_rating_before=entry_a_rating_before,
        entry_b_rating_before=entry_b_rating_before,
        entry_a_rd_before=entry_a_rd_before,
        entry_b_rd_before=entry_b_rd_before,
        entry_a_volatility_before=entry_a_volatility_before,
        entry_b_volatility_before=entry_b_volatility_before,
        entry_a_rating_after=entry_a_rating_after,
        entry_b_rating_after=entry_b_rating_after,
        entry_a_rd_after=entry_a_rd_after,
        entry_b_rd_after=entry_b_rd_after,
        entry_a_volatility_after=entry_a_volatility_after,
        entry_b_volatility_after=entry_b_volatility_after,
    )
    db.add(comparison)
    #await db.commit()
    #await db.refresh(comparison)
    await db.flush()
    return comparison

async def get_comparison_by_id(db: AsyncSession, id: int) -> Comparison | None:
    stmt = select(Comparison).where(Comparison.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_comparisons_by_contest_id(db: AsyncSession, contest_id: int) -> list[Comparison]:
    stmt = select(Comparison).where(Comparison.contest_id == contest_id).order_by(Comparison.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_comparisons_by_voter_user_id(db: AsyncSession, voter_user_id: int) -> list[Comparison]:
    stmt = select(Comparison).where(Comparison.voter_user_id == voter_user_id).order_by(Comparison.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_comparison_by_entry_id(db: AsyncSession, entry_id: int) -> list[Comparison]:
    stmt = (
        select(Comparison)
        .where(Comparison.entry_a_id == entry_id) | (Comparison.entry_b_id == entry_id)
        .order_by(Comparison.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()