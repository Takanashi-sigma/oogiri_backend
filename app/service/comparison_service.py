from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.crud.contest_participation_crud import get_contest_participation_by_user_and_contest_id
from app.crud.entry_crud import get_entry_by_entry_id, update_entry
from app.crud.comparison_crud import create_comparison, get_comparison_by_entry_id, get_comparison_by_id, get_comparisons_by_contest_id, get_comparisons_by_voter_user_id
from app.model.entry_model import Entry
from app.model.contest_participation_model import ContestParticipation
from app.service.glicko_service import rate_1vs1
from app.service.entry_service import update_rating_status
from app.service.contest_participation_service import update_evaluation_count

def get_scores(entry_a_id: int, entry_b_id: int, chosen_entry_id: int) -> tuple[float, float]:
    if chosen_entry_id == entry_a_id:
        return 1.0, 0.0
    return 0.0, 1.0

async def validate_comparison_inputs(
        db: AsyncSession,
        contest_id: int,
        voter_user_id: int,
        entry_a_id: int,
        entry_b_id: int,
        chosen_entry_id: int
) -> tuple[Entry, Entry, ContestParticipation]:
    if entry_a_id == entry_b_id:
        raise HTTPException(status_code=400, detail="entry_a and entry_b must be different")
    
    if chosen_entry_id not in {entry_a_id, entry_b_id}:
        raise HTTPException(status_code=400, detail="chosen_entry must be entry_a or entry_b")
    
    entry_a = await get_entry_by_entry_id(db=db, entry_id=entry_a_id)
    entry_b = await get_entry_by_entry_id(db=db, entry_id=entry_b_id)

    if entry_a is None or entry_b is None:
        raise HTTPException(status_code=404, detail="entry not found")
    
    if entry_a.contest_id != contest_id or entry_b.contest_id != contest_id:
        raise HTTPException(status_code=400, detail="entries do not belong to this contest")
    
    if voter_user_id in {entry_a.user_id, entry_b.user_id}:
        raise HTTPException(status_code=400, detail="you cannot vote for your entry")
    
    voter_participation = await get_contest_participation_by_user_and_contest_id(db=db, user_id=voter_user_id, contest_id=contest_id)
    if voter_participation is None:
        raise HTTPException(status_code=404, detail="contest participation not found")
    
    return entry_a, entry_b, voter_participation


async def create_comparison_service(
            db: AsyncSession, 
            contest_id: int, 
            voter_user_id: int, 
            entry_a_id: int, 
            entry_b_id: int, 
            chosen_entry_id: int
        ):
    entry_a, entry_b, voter_participation = await validate_comparison_inputs(
            db=db, 
            contest_id=contest_id, 
            voter_user_id=voter_user_id,
            entry_a_id=entry_a_id,
            entry_b_id=entry_b_id,
            chosen_entry_id=chosen_entry_id
        )
    score_a, score_b = get_scores(entry_a_id=entry_a.id, entry_b_id=entry_b.id, chosen_entry_id=chosen_entry_id)


    rating_result = rate_1vs1(
        a_rating=entry_a.rating,
        a_rd=entry_a.rd,
        a_volatility=entry_a.volatility,
        b_rating=entry_b.rating,
        b_rd=entry_b.rd,
        b_volatility=entry_b.volatility,
        a_score=score_a
    )
    
    entry_comparison = await create_comparison(
        db=db,
        contest_id=contest_id,
        voter_user_id=voter_participation.user_id,
        entry_a_id=entry_a.id,
        entry_b_id=entry_b.id,
        chosen_entry_id=chosen_entry_id,
        entry_a_rating_before=entry_a.rating,
        entry_b_rating_before=entry_b.rating,
        entry_a_rd_before=entry_a.rd,
        entry_b_rd_before=entry_b.rd,
        entry_a_volatility_before=entry_a.volatility,
        entry_b_volatility_before=entry_b.volatility,
        entry_a_rating_after=rating_result["a_rating"],
        entry_b_rating_after=rating_result["b_rating"],
        entry_a_rd_after=rating_result["a_rd"],
        entry_b_rd_after=rating_result["b_rd"],
        entry_a_volatility_after=rating_result["a_volatility"],
        entry_b_volatility_after=rating_result["b_volatility"],
    )
    await update_rating_status(#update a_rating_status
        db=db,
        entry_id=entry_a.id,
        rating=rating_result["a_rating"],
        rd=rating_result["a_rd"],
        volatility=rating_result["a_volatility"],
        comparisons_count=entry_a.comparisons_count + 1,
        wins=entry_a.wins + (1 if score_a == 1.0 else 0),
        losses=entry_a.losses + (1 if score_a == 0.0 else 0)
    )
    await update_rating_status(#update b_rating status
        db=db,
        entry_id=entry_b.id,
        rating=rating_result["b_rating"],
        rd=rating_result["b_rd"],
        volatility=rating_result["b_volatility"],
        comparisons_count=entry_b.comparisons_count + 1,
        wins=entry_b.wins + (1 if score_b == 1.0 else 0),
        losses=entry_b.losses + (1 if score_b == 0.0 else 0)
    )

    await update_evaluation_count(db=db, user_id=voter_user_id, contest_id=contest_id)#update voters evaluation_count

    await db.commit()
    await db.refresh(entry_comparison)

    return entry_comparison
    
async def get_list_comparisons(db: AsyncSession, contest_id: int):
    result = await get_comparisons_by_contest_id(db=db, contest_id=contest_id)
    if not result:
        raise HTTPException(status_code=404, detail="contest not found")
    return result

async def get_list_comparisons_by_entry_id(db: AsyncSession, entry_id: int):
    result = await get_comparison_by_entry_id(db=db, entry_id=entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="contest not found")
    return result

