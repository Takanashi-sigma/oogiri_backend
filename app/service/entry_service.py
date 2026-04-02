from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.model.contest_model import ContestStatus
from app.crud.contest_crud import get_contest_by_id
from app.crud.contest_participation_crud import get_contest_participation_by_user_and_contest_id
from app.crud.entry_crud import get_entry_by_contest_id, get_entry_by_user_id, create_entry, get_entry_by_user_and_contest_id, update_entry, get_ranking_entries, get_random_two_entries_excluding_user, get_entry_by_entry_id, delete_entry, count_entries_by_contest_id, count_entries_above_me
from app.model.entry_model import Entry
from app.model.contest_participation_model import ContestParticipation
from app.service.contest_participation_service import create_contest_participation, delete_contest_participation


def can_join_ranking(participation: ContestParticipation) -> bool:
    return participation.has_submitted_entry and participation.evaluation_count >= 50



async def entry_contest(db: AsyncSession, contest_id: int, user_id: int, content: str):
    has_entered = await get_entry_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if has_entered:
        raise HTTPException(status_code=400, detail="participation is only once")
    
    await create_contest_participation(db=db, contest_id=contest_id, user_id=user_id)

    participation = await get_contest_participation_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if not participation:
        raise HTTPException(status_code=404, detail="contest participation not found")
    
    contest = await get_contest_by_id(db=db, contest_id=contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="contest not found")

    try:
        entry_contest = await create_entry(db=db, contest_id=contest_id, user_id=user_id, content=content)
        participation.has_submitted_entry = True
        await db.commit()
        await db.refresh(participation)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=409, detail="fail")
    return {
        "id": entry_contest.id,
        "contest_id": entry_contest.contest_id,
        "user_id": entry_contest.user_id,
        "content":  entry_contest.content,
        "rating": entry_contest.rating,
        "rd": entry_contest.rd,
        "volatility": entry_contest.volatility,
        "comparisons_count": entry_contest.comparisons_count,
        "wins": entry_contest.wins, 
        "losses": entry_contest.losses,
        "created_at": entry_contest.created_at,
        "contest_status": contest.status.value
    }

async def get_my_entries(db: AsyncSession, user_id: int) -> list[Entry]:
    result = await get_entry_by_user_id(db=db, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="entry not found")
    return result

async def list_entry_by_contest_id(db: AsyncSession, contest_id: int) -> list[Entry]:
    result = await get_entry_by_contest_id(db=db, contest_id=contest_id)
    if not result:
        raise HTTPException(status_code=404, detail="entry not found")
    return result

async def get_ranking(db: AsyncSession, contest_id: int, offset: int, limit: int) -> list[Entry]:
    result = await get_ranking_entries(db=db, contest_id=contest_id, offset=offset, limit=limit)
    if not result:
        raise HTTPException(status_code=404, detail="ranking not found")
    
    return result

async def get_entry(db: AsyncSession, entry_id: int) -> Entry:
    result = await get_entry_by_entry_id(db=db, entry_id=entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="entry not found")
    return result

async def get_rank_list(db: AsyncSession, contest_id: int, offset: int, limit: int) -> dict:
    entries = await get_ranking_entries(db=db, contest_id=contest_id, offset=offset, limit=limit)
    
    total_count = await count_entries_by_contest_id(db=db, contest_id=contest_id)
    items = []
    for index, entry in enumerate(entries):
        items.append({
            "rank": offset + index + 1,
            "entry_id": entry.id,
            "content": entry.content,
            "rating": entry.rating
        })
    has_more = offset + limit < total_count

    return {
        "items": items,
        "has_more": has_more
    }

async def get_my_ranking(db: AsyncSession, contest_id: int, user_id: int) -> dict:
    my_entry = await get_entry_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if not my_entry:
        raise HTTPException(status_code=404, detail="entry not found")
    above_count = await count_entries_above_me(db=db, contest_id=contest_id, my_rating=my_entry.rating, user_id=user_id)

    return {
        "rank": above_count + 1,
        "entry_id": my_entry.id,
        "content": my_entry.content,
        "rating": my_entry.rating
    }


async def get_specific_entry(db: AsyncSession, user_id: int, contest_id: int) -> Entry:
    result = await get_entry_by_user_and_contest_id(db=db, user_id=user_id, contest_id=contest_id)
    if not result:
        raise HTTPException(status_code=404, detail="entry not found")
    return result

async def get_comparison_candidates(db: AsyncSession, contest_id: int, user_id: int):
    entries = await get_random_two_entries_excluding_user(db=db, contest_id=contest_id, user_id=user_id)

    if len(entries) < 2:
        raise HTTPException(status_code=404, detail="entries must be two comparisons")
    
    return entries

async def update_rating_status(
        db: AsyncSession,
        entry_id: int,
        rating: float,
        rd: float,
        volatility: float,
        comparisons_count: int,
        wins: int,
        losses: int
) -> Entry:
    entry = await db.get(Entry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")
    return await update_entry(
        db=db,
        entry=entry,
        rating=rating,
        rd=rd,
        volatility=volatility,
        comparisons_count=comparisons_count,
        wins=wins,
        losses=losses
    )

async def update_entry_content(db: AsyncSession, user_id: int, contest_id: int, entry_id, new_content: str) -> Entry:
    contest = await get_contest_by_id(db=db, contest_id=contest_id)
    entry = await get_entry_by_entry_id(db=db, entry_id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="entry not_found")
    if not contest:
        raise HTTPException(status_code=404, detail="contest not found")
    if contest.status != ContestStatus.draft:
        raise HTTPException(status_code=401, detail="this contest has alredy started")
    if entry.user_id != user_id:
        raise HTTPException(status_code=401, detail="cannot update others entry")
    result = await update_entry(db=db, entry=entry, content=new_content)
    return result

async def delete_my_entry(db: AsyncSession, entry_id: int, user_id: int) -> None:
    entry = await get_entry_by_entry_id(db=db, entry_id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")
    contest_participation = await get_contest_participation_by_user_and_contest_id(db=db, user_id=user_id, contest_id=entry.contest_id)
    
    if entry.user_id != user_id:
        raise HTTPException(status_code=403, detail="you cant delete this entry")
    await delete_contest_participation(db=db, contest_participation=contest_participation)
    await delete_entry(db=db, entry=entry)
    await db.commit()

